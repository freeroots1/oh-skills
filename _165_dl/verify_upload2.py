#!/usr/bin/env python3
"""verify new UPLOAD candidates - CN sites, real, upload form, admin"""
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
        t = title.group(1).strip()[:30] if title else "?"
        out.append(t)
        out.append("upload=%s" % ('type="file"' in body.lower() or 'multipart' in body.lower()))
        # cms
        for kw, name in [("wp-content", "WP"), ("thinkphp", "TP"), ("dede", "DEDE"),
                         ("pbootcms", "PBOOT"), ("ecms", "EMPIRE"), ("phpcms", "PHPCMS")]:
            if kw in body.lower():
                out.append(name)
        # admin paths
        for p in ["/admin/", "/admin/login.php", "/login.php", "/manage/"]:
            try:
                req2 = urllib.request.Request("http://" + d + p, headers=UA)
                r2 = urllib.request.urlopen(req2, timeout=5)
                b2 = r2.read(3000).decode("utf-8", "ignore")
                if "password" in b2.lower() or "用户名" in b2 or "login" in b2.lower():
                    out.append("ADMIN:%s" % p)
                    break
            except Exception:
                pass
    except urllib.error.HTTPError as e:
        out.append("HTTP%d" % e.code)
    except Exception:
        out.append("ERR")
    return out

doms = ["xinxinjj.com", "xxrwjc.cn", "xybwg.com.cn", "yj-bf.com", "zileijg.com",
        "zhongshengjinshuzhipin.com", "zxjs88.com", "zwzs1688.com"]
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(check, d): d for d in doms}
    for fut in as_completed(futs):
        print(" | ".join(fut.result()), flush=True)
