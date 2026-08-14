#!/usr/bin/env python3
"""fingerprint AH company sites - likely same builder template"""
import urllib.request, re
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def check(d):
    try:
        req = urllib.request.Request("http://" + d + "/", headers=UA)
        r = urllib.request.urlopen(req, timeout=10)
        body = r.read(150000).decode("utf-8", "ignore")
        url = r.geturl()
        title = re.search(r"<title>([^<]*)</title>", body, re.I)
        # fingerprints
        fp = []
        if "wordpress" in body.lower() or "wp-content" in body.lower():
            fp.append("WP")
        if "thinkphp" in body.lower() or "index.php?m=" in body:
            fp.append("TP")
        if "dedecms" in body.lower() or "/plus/" in body.lower():
            fp.append("DEDE")
        if "pbootcms" in body.lower() or "pb_" in body.lower():
            fp.append("PBOOT")
        if "metinfo" in body.lower():
            fp.append("METINFO")
        if "destoon" in body.lower():
            fp.append("DESTOON")
        if "织梦" in body:
            fp.append("织梦")
        if "帝国" in body or "ecms" in body.lower():
            fp.append("EMPIRE")
        if "powered" in body.lower():
            m = re.findall(r'(?:powered|Powered) by[^<]{0,40}', body)
            fp.append("POWERED:" + m[0][:40] if m else "")
        # generator meta
        gen = re.findall(r'<meta[^>]*generator[^>]*content="([^"]+)"', body, re.I)
        if gen:
            fp.append("GEN:" + gen[0][:40])
        # form action / js hints
        t = title.group(1).strip()[:30] if title else ""
        return (d, ",".join(fp) if fp else "-", t, url[:30])
    except Exception as ex:
        return (d, "ERR", "", str(ex)[:25])

doms = ["ahbill.com", "china-haixing.com", "ahzfgg.com", "ahyyhb.net", "ahhubang.com",
        "ahhzlq.com", "ahsjkx.net", "ahxiyy.com", "ahtlt.com.cn", "ahzyhh.com",
        "ahygfz.com", "ahlhby.com"]
with ThreadPoolExecutor(max_workers=12) as ex:
    futs = {ex.submit(check, d): d for d in doms}
    for fut in as_completed(futs):
        d, fp, t, url = fut.result()
        print("%-18s [%s] %s | %s" % (d, fp, t, url), flush=True)
