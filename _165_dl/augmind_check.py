#!/usr/bin/env python3
"""augmind.me /e/admin/ - is it real empire login?"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}

def fetch(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(80000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(3000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

code, body = fetch("http://augmind.me/e/admin/")
print("code=%s size=%d" % (code, len(body)))
title = re.search(r"<title>([^<]*)</title>", body, re.I)
print("title:", title.group(1)[:50] if title else "?")
# login form?
for m in re.finditer(r'<input[^>]*>|<form[^>]*>', body, re.I):
    print("  ", m.group(0)[:120])
# empire login markers
for kw in ["ecms", "EmpireCMS", "登录", "username", "password", "adminlogin"]:
    if kw in body:
        print("MARKER:", kw)
# redirect?
code2, body2 = fetch("http://augmind.me/e/admin/login.php")
print("login.php: %s size=%d" % (code2, len(body2)))
title2 = re.search(r"<title>([^<]*)</title>", body2, re.I)
print("  title:", title2.group(1)[:50] if title2 else "?")
