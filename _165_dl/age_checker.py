#!/usr/bin/env python3
"""批量RDAP查域名年龄，筛选20年以上老域名"""
import urllib.request, json, ssl, sys, os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get_reg_year(domain):
    url = f"https://rdap.verisign.com/com/v1/domain/{domain}"
    try:
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/json")
        r = urllib.request.urlopen(req, timeout=5, context=ctx)
        data = json.loads(r.read())
        for event in data.get("events", []):
            if event.get("eventAction") == "registration":
                date = event.get("eventDate", "")
                return int(date[:4])
    except:
        return None
    return None

# 读取域名列表
with open("/tmp/dom_list.txt") as f:
    domains = [d.strip() for d in f if d.strip()]

print(f"Total .com domains: {len(domains)}", flush=True)

old_sites = []
for i, d in enumerate(domains):
    year = get_reg_year(d)
    if year:
        age = 2026 - year
        if age >= 20:
            old_sites.append((d, year, age))
            print(f"[{i}/{len(domains)}] {d}: {year} ({age}y) !!", flush=True)
        elif age >= 15:
            print(f"[{i}/{len(domains)}] {d}: {year} ({age}y)", flush=True)
    if i % 50 == 0 and i > 0:
        print(f"[{i}/{len(domains)}] progress...", flush=True)

print(f"\n=== 20+ year old domains: {len(old_sites)} ===", flush=True)
for d, y, a in sorted(old_sites, key=lambda x: x[1]):
    print(f"  {d}: {y} ({a}y)")

# 保存结果
with open("/tmp/old20_results.txt", "w") as f:
    for d, y, a in old_sites:
        f.write(f"{d}|{y}|{a}y\n")
