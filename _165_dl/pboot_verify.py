#!/usr/bin/env python3
"""verify pbootcms candidates - real + admin.php + known vuln"""
import urllib.request, re
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def check(d):
    out = [d]
    try:
        req = urllib.request.Request("http://" + d + "/", headers=UA)
        r = urllib.request.urlopen(req, timeout=7)
        body = r.read(100000).decode("utf-8", "ignore")
        url = r.geturl()
        title = re.search(r"<title>([^<]*)</title>", body, re.I)
        is_pboot = "pbootcms" in body.lower() or "pb_" in body.lower() or "p=/" in url.lower() or "/index.php?p=" in body.lower()
        # catch-all check
        try:
            req2 = urllib.request.Request("http://" + d + "/nonexist123.html", headers=UA)
            r2 = urllib.request.urlopen(req2, timeout=5)
            b2 = r2.read(3000)
            catchall = abs(len(b2) - len(body)) < 100
        except Exception:
            catchall = False
        out.append("title=%s pboot=%s catchall=%s" % (title.group(1).strip()[:25] if title else "?", is_pboot, catchall))
        # admin.php
        for p in ["/admin.php", "/admin/", "/index.php/admin/index/login"]:
            try:
                req3 = urllib.request.Request("http://" + d + p, headers=UA)
                r3 = urllib.request.urlopen(req3, timeout=5)
                b3 = r3.read(3000).decode("utf-8", "ignore")
                if "password" in b3.lower() or "用户名" in b3 or "验证码" in b3:
                    out.append("ADMIN:%s" % p)
                    break
            except Exception:
                pass
    except urllib.error.HTTPError as e:
        out.append("HTTP%d" % e.code)
    except Exception as ex:
        out.append("ERR")
    return out

# from web_vuln2 pbootcms candidates (non-hijacked)
doms = ["campnstyle.com", "0do.net", "agence-uni.com", "andisi.cc", "angloiraqi.org",
        "balairungpress.com", "bcn-detectives.com", "bowlwithseoul.com", "catugbio.com",
        "columbiabrotherspowerwashing.com", "environmentalhelp.net", "garagedoors-houstonheights.com",
        "hxgczx.com.cn", "jhnew.com", "jianzhipipefitting.com"]
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(check, d): d for d in doms}
    for fut in as_completed(futs):
        print(" | ".join(fut.result()), flush=True)
