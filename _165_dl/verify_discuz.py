#!/usr/bin/env python3
"""verify Discuz candidates - real forum + version + vuln surface"""
import urllib.request, re
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}

def check(d):
    out = []
    try:
        req = urllib.request.Request("http://" + d + "/", headers=UA)
        r = urllib.request.urlopen(req, timeout=8)
        body = r.read(150000).decode("utf-8", "ignore")
        url = r.geturl()
        title = re.search(r"<title>([^<]*)</title>", body, re.I)
        t = title.group(1).strip()[:35] if title else ""
        # Discuz markers
        markers = []
        for kw in ["discuz", "forum.php", "ucenter", "Powered by Discuz", "X3", "X2", "X1", "dz_"]:
            if kw.lower() in body.lower():
                markers.append(kw)
        # version in meta or footer
        ver = re.search(r'Discuz!\s*(X[\d.]+)', body, re.I) or re.search(r'Powered by Discuz! X(\d\.\d+)', body, re.I)
        out.append((d, "REAL" if markers else "?", t, url[:30], ",".join(markers[:3]), ver.group(1) if ver else ""))
    except urllib.error.HTTPError as e:
        out.append((d, "HTTP%d" % e.code, "", "", "", ""))
    except Exception as ex:
        out.append((d, "ERR", "", str(ex)[:25], "", ""))
    return out

doms = ["dealabc.com", "forum.igclubs.org", "jsclbp.com", "lk0355.com",
        "turksincanada.com", "dismall.com", "0do.net"]
with ThreadPoolExecutor(max_workers=7) as ex:
    futs = {ex.submit(check, d): d for d in doms}
    for fut in as_completed(futs):
        for row in fut.result():
            d, st, t, url, mk, ver = row
            print("%-22s [%s] %s | %s | %s | ver=%s" % (d, st, t, url, mk, ver), flush=True)
