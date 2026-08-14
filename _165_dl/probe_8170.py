#!/usr/bin/env python3
"""批量测81.70段8980/9096目标"""
import urllib.request, http.cookiejar, ssl, re, sys, time
from concurrent.futures import ThreadPoolExecutor

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

ips = ["81.70.184.225","81.70.95.138","81.70.150.138","81.70.252.165","81.70.152.184",
       "81.70.40.16","81.70.71.50","81.70.158.115","81.70.186.157","81.70.248.240",
       "81.70.34.75","81.70.142.148","81.70.116.109","81.70.39.195","81.70.51.143",
       "81.70.53.127","81.70.83.230","81.70.161.35"]

def check(ip):
    for port in [8980, 9096]:
        try:
            req = urllib.request.Request(f"http://{ip}:{port}/", headers={"User-Agent":"Mozilla/5.0"})
            r = urllib.request.urlopen(req, timeout=5, context=ctx)
            body = r.read().decode("utf-8","ignore")
            if "phpStudy" in body or "探针" in body:
                # 查phpMyAdmin
                pma = ""
                try:
                    r2 = urllib.request.urlopen(urllib.request.Request(f"http://{ip}:{port}/phpmyadmin/", headers={"User-Agent":"Mozilla/5.0"}), timeout=4, context=ctx)
                    b2 = r2.read().decode("utf-8","ignore")
                    if "phpMyAdmin" in b2 or "pma_username" in b2:
                        pma = " [phpMyAdmin!]"
                except Exception:
                    pass
                return f"!!! {ip}:{port} phpStudy探针{pma}"
        except Exception:
            pass
    return None

with ThreadPoolExecutor(10) as ex:
    for r in ex.map(check, ips):
        if r: print(r, flush=True)
print("DONE")
