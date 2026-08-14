#!/usr/bin/env python3
"""大规模批量识别phpStudy探针+phpMyAdmin"""
import urllib.request, ssl, sys
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

def check(ip):
    ports = ["80", "8980", "9096"]
    for port in ports:
        try:
            req = urllib.request.Request(f"http://{ip}:{port}/", headers={"User-Agent":"Mozilla/5.0"})
            r = urllib.request.urlopen(req, timeout=3, context=ctx)
            body = r.read().decode("utf-8","ignore")
            if "phpStudy" in body and "探针" in body:
                pma = ""
                try:
                    r2 = urllib.request.urlopen(urllib.request.Request(f"http://{ip}:{port}/phpmyadmin/", headers={"User-Agent":"Mozilla/5.0"}), timeout=2, context=ctx)
                    b2 = r2.read().decode("utf-8","ignore")
                    if "phpMyAdmin" in b2 or "pma_username" in b2:
                        pma = " [phpMyAdmin!]"
                except Exception:
                    pass
                return f"!!! {ip}:{port} phpStudy探针{pma}"
        except Exception:
            pass
    return None

count = 0
with ThreadPoolExecutor(40) as ex:
    for r in ex.map(check, uniq):
        if r:
            print(r, flush=True)
            count += 1
print(f"DONE total={len(uniq)} hits={count}")
