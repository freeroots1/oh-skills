#!/usr/bin/env python3
"""CMS指纹精准采集 — DedeCMS/帝国CMS/Discuz/ThinkPHP/WordPress等"""
import subprocess, re, time, urllib.parse

def bing_search(query, pages=2):
    domains = set()
    encoded = urllib.parse.quote(query)
    
    for page in range(pages):
        first = page * 10 + 1
        url = f"https://cn.bing.com/search?q={encoded}&first={first}&count=10"
        html = subprocess.run(
            ["curl", "-sk", "--connect-timeout", "10", "--max-time", "20",
             "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
             url],
            capture_output=True, text=True, timeout=25
        ).stdout
        
        # Extract domains from search results
        for m in re.finditer(r'<cite[^>]*>(https?://[a-z0-9.-]+\.[a-z]{2,})[^<]*</cite>', html):
            d = re.search(r'https?://([a-z0-9.-]+\.[a-z]{2,})', m.group(1))
            if d and "bing.com" not in d.group(1):
                domains.add(d.group(1).lower())
        
        # Also from h2 links
        for m in re.finditer(r'<a[^>]*href="(https?://[a-z0-9.-]+\.[a-z]{2,})[^"]*"[^>]*>', html):
            d = re.search(r'https?://([a-z0-9.-]+\.[a-z]{2,})', m.group(1))
            if d and "bing.com" not in d.group(1) and "microsoft" not in d.group(1):
                domains.add(d.group(1).lower())
        
        time.sleep(3)
    
    return domains

# ====== CMS指纹搜索 ======
CMS_QUERIES = [
    ("DedeCMS", [
        'intitle:"织梦内容管理系统"',
        '"Powered by DedeCMS"',
        'inurl:/dede/ site:.cn',
    ]),
    ("帝国CMS", [
        'intitle:"帝国CMS"',
        '"Powered by EmpireCMS"',
    ]),
    ("Discuz", [
        '"Powered by Discuz!"',
    ]),
    ("ThinkPHP", [
        'intitle:"ThinkPHP" "Framework"',
        '"X-Powered-By: ThinkPHP" site:.cn',
    ]),
    ("WordPress", [
        'inurl:/wp-admin/ site:.cn',
    ]),
]

# ====== 行业关键词 ======
INDUSTRY_QUERIES = [
    ("教育", 'site:edu.cn inurl:php'),
    ("制造", 'intitle:公司 inurl:product site:.cn'),
    ("医疗", 'inurl:hospital intitle:医院 site:.cn'),
]

all_domains = set()

# CMS搜索
print("=== CMS指纹搜索 ===")
for cms, queries in CMS_QUERIES:
    for q in queries:
        try:
            domains = bing_search(q, pages=1)
            print(f"  {cms}[{q[:30]}]: {len(domains)} domains")
            all_domains.update(domains)
        except Exception as e:
            print(f"  {cms}: FAILED - {e}")

# 行业搜索
print("\n=== 行业搜索 ===")
for name, query in INDUSTRY_QUERIES:
    try:
        domains = bing_search(query, pages=1)
        print(f"  {name}: {len(domains)} domains")
        all_domains.update(domains)
    except Exception as e:
        print(f"  {name}: FAILED - {e}")

# 过滤
final = []
for d in all_domains:
    d = d.lower()
    if d.startswith("www."): d = d[4:]
    if len(d) > 5 and "." in d and len(d) < 60:
        final.append(d)

final = sorted(set(final))

with open("/tmp/cms_targets.txt", "w") as f:
    for d in final: f.write(d + "\n")

print(f"\n{'='*40}")
print(f"Total unique: {len(final)}")
print(f"Saved: /tmp/cms_targets.txt")
for d in final[:30]:
    print(f"  {d}")
