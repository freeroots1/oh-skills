#!/usr/bin/env python3
"""Bing搜索采集老版本CMS站点"""
import subprocess, re, time, urllib.parse

def bing_search(query, pages=3):
    all_domains = set()
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
        
        # bing在 cite 标签里放URL
        for m in re.finditer(r'<cite[^>]*>(https?://[^<]+)</cite>', html):
            domain = re.search(r'https?://([a-z0-9.-]+\.[a-z]{2,})', m.group(1))
            if domain:
                d = domain.group(1).lower()
                if len(d) > 5 and "bing.com" not in d:
                    all_domains.add(d)
        
        # 也可以在 a标签里
        for m in re.finditer(r'href="(https?://[a-z0-9.-]+\.[a-z]{2,})[^"]*"', html):
            d = re.search(r'https?://([a-z0-9.-]+\.[a-z]{2,})', m.group(1))
            if d and "bing.com" not in d.group(1):
                all_domains.add(d.group(1).lower())
        
        time.sleep(2)
    
    return all_domains

# ====== 搜索列表 ======
DORKS = [
    ("PHP5.2", '"PHP/5.2" site:.cn'),
    ("PHP5.3", '"PHP/5.3" site:.cn'),
    ("PHP5.4", '"PHP/5.4" site:.cn'),
    ("DedeCMS", '"Powered by DedeCMS"'),
    ("ThinkPHP3", '"ThinkPHP" "Framework" site:.cn'),
    ("IIS6", '"Microsoft-IIS/6.0" site:.cn'),
    ("Apache2.2", '"Apache/2.2" site:.cn'),
]

all_found = set()

for name, dork in DORKS:
    try:
        domains = bing_search(dork, pages=2)
        print(f"{name}: {len(domains)} domains")
        all_found.update(domains)
    except Exception as e:
        print(f"{name}: FAILED - {e}")

# 保存
with open("/tmp/bing_old_targets.txt", "w") as f:
    for d in sorted(all_found):
        f.write(d + "\n")

print(f"\nTotal unique: {len(all_found)}")
print("Saved: /tmp/bing_old_targets.txt")
for d in sorted(all_found)[:25]:
    print(f"  {d}")
