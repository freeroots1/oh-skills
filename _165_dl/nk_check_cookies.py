#!/usr/bin/env python3
"""naukrigov: check if login POST actually set auth cookies despite CF"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Cache-Control": "no-cache", "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
}
BASE = "https://naukrigov.com"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch(url, data=None, timeout=20, allow_redirect=False):
    h = dict(UA)
    if data is not None:
        h["Content-Type"] = "application/x-www-form-urlencoded"
        h["Origin"] = BASE
        h["Referer"] = BASE + "/wp-login.php"
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    o = op
    if not allow_redirect:
        o = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), NoRedirect)
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = o.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, url, e.read().decode("utf-8", "ignore"), dict(e.headers)
    except Exception as ex:
        return 0, url, str(ex), {}

# 1. GET
code, final, body, hdrs = fetch(BASE + "/wp-login.php")
print("1) GET:", code, "cookies:", [c.name for c in cj])

# 2. POST no redirect - capture Location + cookies
data = urllib.parse.urlencode({
    "log": "admin", "pwd": "admin123", "wp-submit": "Log In",
    "redirect_to": BASE + "/wp-admin/", "testcookie": "1"})
code, final, resp, hdrs = fetch(BASE + "/wp-login.php", data=data)
print("2) POST:", code, final)
print("   Location:", hdrs.get("Location", "NONE"))
print("   cookies now:", [(c.name, c.value[:30]) for c in cj])

# 3. if auth cookie present, we are IN - try wp-admin with the cookie via direct source IP?
# check cookie names
auth_cookies = [c for c in cj if "wordpress_logged_in" in c.name or "wordpress_sec" in c.name]
print("   auth cookies:", [c.name for c in auth_cookies])
