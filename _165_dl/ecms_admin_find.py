#!/usr/bin/env python3
"""find EmpireCMS admin - probe common paths on home page + variants"""
import urllib.request, re
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}

def fetch(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(80000)
    except urllib.error.HTTPError as e:
        return e.code, e.read(3000)
    except Exception:
        return 0, b""

def probe(d):
    scheme = "https://" if d in ("china-qualityinspection.com", "dhyindustry.com", "uy-mold.com", "treasurebeingyou.com") else "http://"
    out = [d]
    # extract links from home for admin hints
    code, body = fetch(scheme + d + "/")
    hl = body.decode("utf-8", "ignore")
    links = set(re.findall(r'href=["\']([^"\']+)["\']', hl))
    admin_links = [l for l in links if any(k in l.lower() for k in ["admin", "manage", "e/admin", "houtai", "login", "empire"])]
    out.append("admin_links: %s" % admin_links[:5])
    # common empire admin paths
    for p in ["/e/admin/", "/e/manager/", "/e/admin/index.php", "/admin/", "/houtai/",
              "/e/", "/e/install/index.php", "/e/action/", "/e/member/"]:
        c, b = fetch(scheme + d + p)
        if c == 200 and len(b) > 400:
            out.append("%s:%d" % (p, len(b)))
    return out

doms = ["treasurebeingyou.com", "sdgbgg.com", "china-qualityinspection.com", "uy-mold.com", "dhyindustry.com"]
with ThreadPoolExecutor(max_workers=5) as ex:
    futs = {ex.submit(probe, d): d for d in doms}
    for fut in as_completed(futs):
        print(" | ".join(fut.result()), flush=True)
