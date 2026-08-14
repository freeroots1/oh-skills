#!/usr/bin/env python3
"""批量测8080/8980/9096目标: phpStudy探针+phpMyAdmin"""
import urllib.request, http.cookiejar, ssl, re, sys, time
from concurrent.futures import ThreadPoolExecutor

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

# 目标: host:port
targets = [
    ("hotgamehl.com","124.95.136.140","8080"), ("mingfucloud.com","39.105.120.117","8080"),
    ("weiyi.com","47.104.146.152","8080"), ("dadongwu.com","60.191.141.84","8080"),
    ("ygbx.com","101.37.42.237","8080"), ("dingliangame.com","47.243.139.128","8080"),
    ("ailibang.com","157.0.3.36","8080"), ("wantiangroup.com","124.232.137.110","8080"),
    ("truesing.com","101.43.14.236","8080"), ("aiqiangua.com","47.114.94.16","8080"),
    ("apspharm.com","47.94.105.108","8080"), ("basicfinder.com","114.67.228.66","8080"),
]

def check_probe(target):
    name, ip, port = target
    try:
        req = urllib.request.Request(f"http://{ip}:{port}/", headers={"User-Agent":"Mozilla/5.0","Host":name})
        r = urllib.request.urlopen(req, timeout=6, context=ctx)
        body = r.read().decode("utf-8","ignore")
        if "phpStudy" in body or "探针" in body:
            # 检查phpMyAdmin
            has_pma = False
            try:
                r2 = urllib.request.urlopen(urllib.request.Request(f"http://{ip}:{port}/phpmyadmin/", headers={"User-Agent":"Mozilla/5.0","Host":name}), timeout=5, context=ctx)
                b2 = r2.read().decode("utf-8","ignore")
                has_pma = "phpMyAdmin" in b2 or "pma_username" in b2
            except Exception:
                pass
            return f"!!! {name}({ip}:{port}) phpStudy探针 phpMyAdmin={has_pma}"
    except Exception:
        pass
    return None

with ThreadPoolExecutor(8) as ex:
    for r in ex.map(check_probe, targets):
        if r: print(r, flush=True)
print("DONE")
