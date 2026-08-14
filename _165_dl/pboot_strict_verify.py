#!/usr/bin/env python3
"""re-verify 5 pboot LOGIN-HIT with STRICT backend marker check"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
SITES = ["http://indexsummit6.com", "http://insightsmonitor.com", "http://mendilab.com",
         "http://www.indexsummit6.com", "http://www.mendilab.com"]
STRICT = ["系统设置", "内容管理", "栏目管理", "数据管理", "用户管理", "后台首页",
          "pbootcms", "模板管理", "附件管理", "nav-group", "layui"]

def fetch(url, timeout=10, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"} if data else UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

for site in SITES:
    # login attempt with proper flow
    code, body = fetch(site + "/admin.php")
    has_login = 'name="user"' in body or 'name="username"' in body or 'type="password"' in body
    print("=== %s ===" % site, flush=True)
    print("  has_login_form: %s size=%d" % (has_login, len(body)), flush=True)
    if not has_login:
        # try /admin/ path
        code, body = fetch(site + "/admin/")
        print("  /admin/: size=%d has_login=%s" % (len(body), 'type="password"' in body or 'name="user"' in body), flush=True)
    # login with empty code
    data = urllib.parse.urlencode({"user": "admin", "password": "admin", "code": ""})
    code, body = fetch(site + "/admin.php", data=data)
    strict_hits = [m for m in STRICT if m in body]
    print("  after-login strict markers: %s" % strict_hits[:5], flush=True)
    if strict_hits:
        print("  !!! REAL BACKEND", flush=True)
