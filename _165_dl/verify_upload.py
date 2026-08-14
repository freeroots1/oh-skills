#!/usr/bin/env python3
"""verify UPLOAD candidates - find real attackable (non-catchall, CN or small sites)"""
import urllib.request, re
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def check(d):
    try:
        req = urllib.request.Request("http://" + d + "/", headers=UA)
        r = urllib.request.urlopen(req, timeout=8)
        url = r.geturl()
        body = r.read(80000).decode("utf-8", "ignore")
        title = re.search(r"<title>([^<]*)</title>", body, re.I)
        t = title.group(1).strip()[:35] if title else ""
        # catch-all: nonsense path same size
        try:
            req2 = urllib.request.Request("http://" + d + "/nonexist12345xyz.html", headers=UA)
            r2 = urllib.request.urlopen(req2, timeout=6)
            b2 = r2.read(3000).decode("utf-8", "ignore")
            catchall = len(b2) > 500 and abs(len(b2) - len(body)) < 100
        except Exception:
            catchall = False
        # find upload forms
        has_upload = 'type="file"' in body or 'multipart/form-data' in body
        return (d, "CATCHALL" if catchall else "REAL", t, url[:40], has_upload)
    except urllib.error.HTTPError as e:
        return (d, "HTTP%d" % e.code, "", "", False)
    except Exception as ex:
        return (d, "ERR", "", str(ex)[:30], False)

# CN + small candidates from UPLOAD list
doms = ["ahbill.com", "ahhubang.com", "ahhzlq.com", "ahlhby.com", "ahsjkx.net",
        "ahtlt.com.cn", "ahxiyy.com", "ahygfz.com", "ahyyhb.net", "ahzfgg.com",
        "ahzyhh.com", "ceieac.com", "china-haixing.com", "chunyicanyin.com",
        "coolfacelife.com", "beachfamilydoctors.com", "bellmontrestaurant.com",
        "brehnelaw.com", "camarillocarcare.com", "childrenshaven.com",
        "connertoncooking.com", "alorica.com", "annaksalon.com", "apiject.com",
        "ardns.net", "assetintelwp.com", "backstagemilano.com", "bellehairextensions.com"]
with ThreadPoolExecutor(max_workers=14) as ex:
    futs = {ex.submit(check, d): d for d in doms}
    for fut in as_completed(futs):
        d, status, t, url, hu = fut.result()
        print("%s [%s] %s | %s | upload=%s" % (d, status, t, url, hu), flush=True)
