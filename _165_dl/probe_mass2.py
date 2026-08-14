#!/usr/bin/env python3
"""大规模批量识别phpStudy探针v2(带进度)"""
import urllib.request, ssl, sys, time
from concurrent.futures import ThreadPoolExecutor

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

ips = []
for line in open("/tmp/ps207_ips.txt"):
    parts = line.split()
    if len(parts) >= 2:
        ips.append(parts[1])

seen = set()
uniq = []
for ip in ips:
    if ip not in seen:
        seen.add(ip)
        uniq.append(ip)
print(f"unique={len(uniq)}", flush=True)

def check(ip):
    for port in ["80", "8980", "9096"]:
        try:
            req = urllib.request.Request(f"http://{ip}:{port}/", headers={"User-Agent":"Mozilla/5.0"}, method="GET")
            r = urllib.request.urlopen(req, timeout=2.5, context=ctx)
            body = r.read(5000).decode("utf-8","ignore")
            if "phpStudy" in body and "探针" in body:
                pma = ""
                try:
                    r2 = urllib.request.urlopen(urllib.request.Request(f"http://{ip}:{port}/phpmyadmin/", headers={"User-Agent":"Mozilla/5.0"}), timeout=2, context=ctx)
                    b2 = r2.read(2000).decode("utf-8","ignore")
                    if "phpMyAdmin" in b2 or "pma_username" in b2:
                        pma = " [phpMyAdmin!]"
                except Exception:
                    pass
                return f"!!! {ip}:{port} phpStudy探针{pma}"
        except Exception:
            pass
    return None

count = 0
done = 0
with ThreadPoolExecutor(60) as ex:
    for r in ex.map(check, uniq):
        done += 1
        if done % 2000 == 0:
            print(f"[进度] {done}/{len(uniq)} hits={count}", flush=True)
        if r:
            print(r, flush=True)
            count += 1
print(f"DONE total={len(uniq)} hits={count}", flush=True)
