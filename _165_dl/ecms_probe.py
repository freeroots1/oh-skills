#!/usr/bin/env python3
"""EmpireCMS vuln probes on 7 real sites - admin path + known vuln endpoints"""
import urllib.request, re
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def fetch(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, len(r.read(50000))
    except urllib.error.HTTPError as e:
        return e.code, len(e.read(3000))
    except Exception:
        return 0, 0

def probe(d):
    out = [d]
    # admin paths
    for p in ["/e/admin/", "/e/admin/index.php", "/e/admin/login.php", "/e/install/",
              "/e/member/login/", "/e/action/ListInfo.php", "/e/admin/ecmsadmin.php"]:
        code, sz = fetch("http://" + d + p)
        if code == 200 and sz > 500:
            out.append("%s:%d" % (p, sz))
    return out

doms = ["china-qualityinspection.com", "dhyindustry.com", "sdgbgg.com",
        "sidazdh.com", "uy-mold.com", "www.2632.net", "treasurebeingyou.com"]
with ThreadPoolExecutor(max_workers=7) as ex:
    futs = {ex.submit(probe, d): d for d in doms}
    for fut in as_completed(futs):
        r = fut.result()
        print(" | ".join(r), flush=True)
