#!/usr/bin/env python3
"""批量测80端口phpStudy探针"""
import urllib.request, ssl, sys
from concurrent.futures import ThreadPoolExecutor

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

ips = [l.strip() for l in open("/tmp/ps80_ips2.txt") if l.strip()]

def check(ip):
    try:
        req = urllib.request.Request(f"http://{ip}/", headers={"User-Agent":"Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=2.5, context=ctx)
        body = r.read(3000).decode("utf-8","ignore")
        if "phpStudy" in body and "探针" in body:
            pma = ""
            try:
                r2 = urllib.request.urlopen(urllib.request.Request(f"http://{ip}/phpmyadmin/", headers={"User-Agent":"Mozilla/5.0"}), timeout=2, context=ctx)
                b2 = r2.read(1500).decode("utf-8","ignore")
                if "phpMyAdmin" in b2 or "pma_username" in b2:
                    pma = " [phpMyAdmin!]"
            except Exception:
                pass
            return f"!!! {ip} phpStudy探针{pma}"
    except Exception:
        pass
    return None

count = 0
done = 0
with ThreadPoolExecutor(80) as ex:
    for r in ex.map(check, ips):
        done += 1
        if done % 3000 == 0:
            print(f"[进度] {done}/{len(ips)} hits={count}", flush=True)
        if r:
            print(r, flush=True)
            count += 1
print(f"DONE total={len(ips)} hits={count}", flush=True)
