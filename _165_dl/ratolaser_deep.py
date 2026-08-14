#!/usr/bin/env python3
"""ratoplaser.com - EmpireCMS deep probe: admin paths + frontend"""
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

code, body = fetch("http://ratoplaser.com/")
print("home: %s size=%d" % (code, len(body)))
title = re.search(r"<title>([^<]*)</title>", body, re.I)
print("title:", title.group(1)[:40] if title else "?")
# all links for admin/dynamic
links = set(re.findall(r'href=["\']([^"\']+)["\']', body))
admin_links = [l for l in links if any(k in l.lower() for k in ["admin", "e/", "manage", "login", "empire"])]
print("admin links:", admin_links[:8])
dyn = set(re.findall(r'([\w./-]+\.php\?[\w]+=[\w]+)', body))
print("dyn:", list(dyn)[:8])
# ecms paths
for p in ["/e/admin/", "/e/admin/login.php", "/e/admin/index.php", "/e/", "/e/member/",
          "/e/action/ShowInfo.php?classid=1&id=1", "/e/action/ListInfo.php?classid=1"]:
    c, b = fetch("http://ratoplaser.com" + p)
    marker = ""
    if "密码" in b or "login" in b.lower() or "username" in b.lower():
        marker = " LOGIN!"
    print("  %s: %s size=%d%s" % (p[:45], c, len(b), marker), flush=True)
