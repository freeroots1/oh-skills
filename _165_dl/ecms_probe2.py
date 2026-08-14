#!/usr/bin/env python3
"""ecms probe v2 - https + follow redirects + check content type"""
import urllib.request, re
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}

def fetch(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        body = r.read(60000)
        final = r.geturl()
        return r.status, len(body), final, body
    except urllib.error.HTTPError as e:
        return e.code, len(e.read(3000)), url, b""
    except Exception:
        return 0, 0, url, b""

def probe(d):
    out = [d]
    # find real scheme
    for scheme in ["http://", "https://"]:
        code, sz, final, body = fetch(scheme + d + "/")
        if code == 200 and sz > 2000:
            # check home for ecms markers
            is_ecms = b"ecms" in body.lower() or b"e/data" in body.lower() or b"empirecms" in body.lower()
            title = re.search(rb"<title>([^<]*)</title>", body, re.I)
            out.append("home:%d ecms=%s title=%s" % (sz, is_ecms, title.group(1).decode('utf-8','ignore')[:25] if title else "?"))
            # admin paths
            for p in ["/e/admin/", "/e/admin/login.php", "/e/install/", "/e/admin/"]:
                c2, s2, f2, b2 = fetch(scheme + d + p)
                if c2 == 200 and s2 > 300 and s2 != sz:
                    out.append("%s:%d" % (p, s2))
            break
    return out

doms = ["china-qualityinspection.com", "dhyindustry.com", "sdgbgg.com",
        "uy-mold.com", "www.2632.net", "treasurebeingyou.com"]
with ThreadPoolExecutor(max_workers=6) as ex:
    futs = {ex.submit(probe, d): d for d in doms}
    for fut in as_completed(futs):
        print(" | ".join(fut.result()), flush=True)
