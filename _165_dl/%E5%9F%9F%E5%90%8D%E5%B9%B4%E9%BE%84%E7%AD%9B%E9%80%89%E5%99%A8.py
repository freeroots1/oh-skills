#!/usr/bin/env python3
"""
RDAP域名年龄筛选器 — 只保留20年以上老域名
原理: RDAP协议公开免费,无需API Key
"""
import subprocess, json, sys, time, re
from datetime import date

def query_rdap(domain):
    """查域名注册日期"""
    try:
        r = subprocess.run(['curl','-sk','--connect-timeout','10',
            f'https://rdap.org/domain/{domain}'],
            capture_output=True,text=True,timeout=12)
        if r.returncode != 0 or not r.stdout: return None
        data = json.loads(r.stdout)
        created = ""
        for e in data.get("events",[]):
            if e.get("eventAction") == "registration":
                created = e.get("eventDate","")[:10]
        if created:
            days = (date.today() - date.fromisoformat(created)).days
            return {"domain":domain,"created":created,"days":days,"years":round(days/365.25,1)}
    except: pass
    return None

# 输入: 从采集器来的域名列表
input_file = sys.argv[1] if len(sys.argv)>1 else "/tmp/collected_domains.txt"
domains = [l.strip() for l in open(input_file) if l.strip() and not l.startswith('#')]

print(f"查询 {len(domains)} 个域名年龄...")
old, young, failed = [], [], []

for i, d in enumerate(domains):
    r = query_rdap(d)
    if r:
        if r["years"] >= 20:
            old.append(r)
            print(f"  ✅ {d}: {r['years']}年 ({r['created']})")
        else:
            young.append(r)
        if (i+1) % 20 == 0: print(f"  ... {i+1}/{len(domains)}")
    else:
        failed.append(d)
    time.sleep(0.3)

# 保存结果
with open("/tmp/old_domains.txt","w") as f:
    for r in sorted(old, key=lambda x:x["days"], reverse=True):
        f.write(f"{r['domain']}\n")

print(f"\n{'='*50}")
print(f"20年以上: {len(old)} | 20年以下: {len(young)} | 失败: {len(failed)}")
if old:
    print(f"→ /tmp/old_domains.txt")
    for r in old[:10]: print(f"  {r['domain']}: {r['years']}年")
