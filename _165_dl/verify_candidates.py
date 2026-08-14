#!/usr/bin/env python3
"""quick verify DedeCMS/TP/Pboot real candidates - find attackable"""
import urllib.request, re
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def check(d):
    try:
        req = urllib.request.Request("http://" + d + "/", headers=UA)
        r = urllib.request.urlopen(req, timeout=8)
        url = r.geturl()
        body = r.read(50000).decode("utf-8", "ignore")
        title = re.search(r"<title>([^<]*)</title>", body, re.I)
        t = title.group(1).strip()[:35] if title else ""
        # catch-all check: probe a nonsense path
        req2 = urllib.request.Request("http://" + d + "/nonexist12345xyz.html", headers=UA)
        r2 = urllib.request.urlopen(req2, timeout=6)
        b2 = r2.read(3000).decode("utf-8", "ignore")
        same = len(b2) > 500 and abs(len(b2) - len(body)) < 100
        return (d, "REAL" if not same else "CATCHALL", t, url[:40], len(body), len(b2))
    except urllib.error.HTTPError as e:
        return (d, "HTTP%d" % e.code, "", "", 0, 0)
    except Exception as ex:
        return (d, "ERR", "", str(ex)[:30], 0, 0)

doms = ["ahdscw.com", "ahyxfh.com", "baiinfo.com", "bojiejinrong.com", "aoccit.com",
        "anzerclub.com", "besson-tools.com", "coolfacelife.com", "diqian.com",
        "dh-forging.com", "andisi.cc", "catugbio.com", "jhnew.com", "hxgczx.com.cn",
        "jianzhipipefitting.com", "0do.net", "360led.net", "3kak.com"]
with ThreadPoolExecutor(max_workers=12) as ex:
    futs = {ex.submit(check, d): d for d in doms}
    for fut in as_completed(futs):
        d, status, t, url, s1, s2 = fut.result()
        print("%s [%s] %s | %s | size=%d/%d" % (d, status, t, url, s1, s2), flush=True)
