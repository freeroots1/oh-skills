#!/usr/bin/env python3
"""new empire CMS: augmind.me, ratoplaser.com, bungaytrust.com - probe + admin"""
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

for d in ["augmind.me", "ratoplaser.com", "bungaytrust.com"]:
    print("=== %s ===" % d, flush=True)
    code, body = fetch("http://" + d + "/")
    title = re.search(r"<title>([^<]*)</title>", body, re.I)
    print("  home: %s size=%d title=%s" % (code, len(body), title.group(1)[:30] if title else "?"), flush=True)
    ecms = "ecms" in body.lower() or "e/data" in body.lower()
    print("  ecms marker:", ecms, flush=True)
    # admin paths
    for p in ["/e/admin/", "/e/admin/index.php", "/e/admin/login.php", "/e/install/"]:
        c, b = fetch("http://" + d + p)
        if c == 200 and len(b) > 300:
            print("  %s: %s size=%d" % (p, c, len(b)), flush=True)
    # dynamic urls
    dyn = set(re.findall(r'([\w./-]+\.php\?[\w]+=[\w]+)', body))
    print("  dyn:", list(dyn)[:5], flush=True)
