#!/usr/bin/env python3
"""confirm pboot hits - check for backend menu markers"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
SITES = ["http://indexsummit6.com", "http://insightsmonitor.com", "http://mendilab.com"]
MARKERS = ["系统设置", "内容管理", "栏目管理", "数据管理", "用户管理", "后台首页",
           "index/index", "pbootcms", "退出登录", "修改密码", "模板管理", "附件管理"]

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

for site in SITES:
    print("=== %s ===" % site, flush=True)
    code, body = fetch(site + "/admin.php")
    found = [m for m in MARKERS if m in body]
    print("  size=%d markers=%s" % (len(body), found[:8]), flush=True)
    # title
    t = re.search(r"<title>([^<]*)</title>", body, re.I)
    print("  title:", t.group(1)[:50] if t else "?", flush=True)
    # check if it's the login page (has user/password inputs)
    has_login_form = 'type="password"' in body or 'name="password"' in body or 'name="user"' in body
    print("  has_login_form:", has_login_form, flush=True)
