#!/usr/bin/env python3
"""dealabc Discuz: proper login flow (get home first for formhash cookie)"""
import urllib.request, urllib.parse, re, http.cookiejar, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://www.dealabc.com"

def get_opener():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

def fetch(op, url, timeout=10, data=None, referer=None):
    h = {**UA}
    if data: h["Content-Type"] = "application/x-www-form-urlencoded"
    if referer: h["Referer"] = referer
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

# proper flow: home -> get formhash -> admin login
op = get_opener()
code, final, body = fetch(op, HOST + "/")
print("home: %s size=%d" % (code, len(body)))
m = re.search(r'formhash=([a-f0-9]+)', body)
home_fh = m.group(1) if m else ""
print("home formhash:", home_fh)

code, final, body = fetch(op, HOST + "/admin.php")
print("admin.php: %s size=%d" % (code, len(body)))
# formhash in admin page
m2 = re.search(r'name="formhash" value="([a-f0-9]+)"', body) or re.search(r'formhash=([a-f0-9]+)', body)
admin_fh = m2.group(1) if m2 else ""
print("admin formhash:", admin_fh)

# try login with either formhash
for fh in [admin_fh, home_fh]:
    if not fh:
        continue
    data = urllib.parse.urlencode({"username": "admin", "password": "admin123", "formhash": fh, "submit": "登录"})
    code, final, body = fetch(op, HOST + "/admin.php?action=login", data=data, referer=HOST + "/admin.php")
    ok = "退出" in body or "admincp" in body or "action=logout" in body or "框架" in body
    print("login with fh=%s: code=%s final=%s ok=%s size=%d" % (fh[:8], code, final[:50], ok, len(body)))
    if ok:
        break
