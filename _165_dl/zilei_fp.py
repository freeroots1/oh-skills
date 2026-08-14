#!/usr/bin/env python3
"""zileijg.com - CMS fingerprint + admin login form + upload point"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://zileijg.com"

def fetch(url, timeout=10, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"} if data else UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

# home fingerprint
code, body = fetch(HOST + "/")
print("home: %s size=%d" % (code, len(body)))
for kw in ["wp-content", "thinkphp", "dede", "pbootcms", "ecms", "phpcms", "帝国", "织梦", "metinfo", "destoon"]:
    if kw in body.lower():
        print("  CMS:", kw)
# upload form
for m in re.finditer(r'<form[^>]*>|<input[^>]*type=["\']file["\']', body, re.I):
    print("  form:", m.group(0)[:100])

# admin page
print("\n=== /admin/ ===")
code, body = fetch(HOST + "/admin/")
print("code=%s size=%d" % (code, len(body)))
for m in re.finditer(r'<input[^>]*>|<form[^>]*>', body, re.I):
    print("  ", m.group(0)[:120])
title = re.search(r"<title>([^<]*)</title>", body, re.I)
print("title:", title.group(1) if title else "?")
