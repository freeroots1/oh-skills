#!/usr/bin/env python3
"""naukrigov login from 165 with Cache-Control: no-cache bypass"""
import urllib.request, urllib.parse, re, http.cookiejar, sys

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
}
BASE = "https://naukrigov.com"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch(url, data=None, timeout=20):
    h = dict(UA)
    if data is not None:
        h["Content-Type"] = "application/x-www-form-urlencoded"
        h["Origin"] = BASE
        h["Referer"] = BASE + "/wp-login.php"
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read().decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

# 1. GET login
code, final, body = fetch(BASE + "/wp-login.php")
print("1) GET:", code, final, "size", len(body), "has_login:", "user_login" in body)

# 2. POST login
data = urllib.parse.urlencode({
    "log": "admin", "pwd": "admin123", "wp-submit": "Log In",
    "redirect_to": BASE + "/wp-admin/", "testcookie": "1"})
code, final, resp = fetch(BASE + "/wp-login.php", data=data)
print("2) POST:", code, final, "size", len(resp))
print("   title:", re.search(r"<title>([^<]*)</title>", resp).group(1) if "<title>" in resp else "?")
print("   login_error:", "login_error" in resp)

# 3. wp-admin
code, final, body3 = fetch(BASE + "/wp-admin/")
print("3) admin:", code, final, "size", len(body3))
print("   title:", re.search(r"<title>([^<]*)</title>", body3).group(1) if "<title>" in body3 else "?")
print("   is_upgrade:", "upgrade" in final or "Database Update" in body3)
print("   dash markers:", {k: (k in body3.lower()) for k in ["dashboard", "wp-admin-bar", "仪表盘"]})

# 4. if upgrade, run it
if "upgrade" in final or "Database Update" in body3:
    up = final if "upgrade" in final else BASE + "/wp-admin/upgrade.php"
    code, final4, body4 = fetch(up + ("&" if "?" in up else "?") + "step=1")
    print("4) upgrade:", code, final4, "size", len(body4))

# 5. dashboard again
code, final, body5 = fetch(BASE + "/wp-admin/")
print("5) dash:", code, final, "size", len(body5))
print("   title:", re.search(r"<title>([^<]*)</title>", body5).group(1) if "<title>" in body5 else "?")
print("   markers:", {k: (k in body5.lower()) for k in ["dashboard", "wp-admin-bar", "仪表盘", "user_login"]})
if "仪表盘" in body5 or "dashboard" in body5.lower():
    open("/tmp/nk_dash_final.html", "w").write(body5)
    print(">>> DASHBOARD SAVED")
