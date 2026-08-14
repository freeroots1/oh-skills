#!/usr/bin/env python3
"""批量IP反查域名(rapiddns)"""
import urllib.request, ssl, re, json, sys
from concurrent.futures import ThreadPoolExecutor

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

ips = []
for line in open("/tmp/cscan_ips.txt"):
    parts = line.split()
    if parts and re.match(r"^\d+\.\d+\.\d+\.\d+$", parts[0]):
        ips.append(parts[0])

def reverse(ip):
    try:
        req = urllib.request.Request(f"https://rapiddns.io/sameip/{ip}?full=1", headers={"User-Agent":"Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=10, context=ctx)
        html = r.read().decode("utf-8","ignore")
        # 提取域名
        domains = re.findall(r'<td>([a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,})</td>', html)
        # 去重过滤
        seen = set()
        result = []
        for d in domains:
            d = d.lower()
            if d not in seen and "." in d and not d.endswith((".png",".jpg",".css",".js")):
                seen.add(d)
                result.append(d)
        return ip, result
    except Exception as e:
        return ip, []

with ThreadPoolExecutor(10) as ex:
    results = list(ex.map(reverse, ips))

with open("/tmp/reverse_domains.txt", "w") as f:
    for ip, domains in results:
        if domains:
            f.write(f"{ip} | {','.join(domains[:20])}\n")
            print(f"{ip} | {','.join(domains[:10])}", flush=True)
print(f"DONE total_ips={len(ips)} with_domains={sum(1 for _,d in results if d)}")
