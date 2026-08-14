#!/usr/bin/env python3
"""zhongsheng - REAL login flow: find actual admin login form + captcha"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://zhongshengjinshuzhipin.com"

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

op, cj = get_opener()
# the admin login is at index.php?g=admin&m=public&a=login (ThinkPHP style)
for p in ["/index.php?g=admin&m=public&a=login", "/admin/index.php?g=admin&m=public&a=login",
          "/index.php/Admin/Public/login", "/admin.php?g=admin&m=public&a=login"]:
    code, final, body = fetch(op, HOST + p)
    has_login = "username" in body.lower() or "密码" in body or "验证码" in body
    print("%s: %s size=%d login=%s" % (p[:55], code, len(body), has_login), flush=True)
    if has_login:
        print("  fields:", re.findall(r'<input[^>]*name=["\']([^"\']+)["\']', body)[:6])
        print("  captcha:", re.findall(r'(captcha|verify|code)[^"\']*', body, re.I)[:3])
