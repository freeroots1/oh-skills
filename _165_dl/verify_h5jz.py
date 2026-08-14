#!/usr/bin/env python3
"""verify h5jz.net wp-login with full cookie session, print markers"""
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

code, final, body = fetch("http://h5jz.net/wp-login.php")
print("1) GET wp-login:", code, final, "size", len(body))
login_url = final if final.startswith("http") else "http://h5jz.net/wp-login.php"
print("   login_url:", login_url)

# try password from the hit
payload = {"log": "admin", "pwd": "12345678", "wp-submit": "Log In",
           "redirect_to": re.sub(r"https?://", "http://", login_url).replace("wp-login.php", "wp-admin/"),
           "testcookie": "1"}
code2, final2, resp = fetch(login_url, data=urllib.parse.urlencode(payload))
print("2) POST login:", code2, final2, "size", len(resp))
print("   resp has 'login_error':", "login_error" in resp)
print("   resp has 'dashboard':", "dashboard" in resp.lower())

# now GET wp-admin with same session
admin_url = final2 if "wp-admin" in final2 else re.sub(r"wp-login\.php.*", "wp-admin/", login_url)
code3, final3, body3 = fetch(admin_url)
print("3) GET wp-admin:", code3, final3, "size", len(body3))
markers = ["dashboard", "仪表盘", "dashicons", "wp-admin-bar", "user_login", "wp-login",
           "wp-admin/css", "登录", "Log In"]
for kw in markers:
    print("   contains %-14s:" % kw, kw in body3.lower())
# title
m = re.search(r"<title>([^<]*)</title>", body3, re.I)
print("   title:", m.group(1) if m else "N/A")

# try wrong password to compare
op2 = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
code4, final4, body4 = fetch2 = None
