#!/usr/bin/env python3
"""采集老旧漏洞网站 — FOFA免费搜索"""
import subprocess, re, time, base64, sys

def fofa_search(query, pages=2):
    qb64 = base64.b64encode(query.encode()).decode()
    all_domains = set()
    
    for page in range(1, pages+1):
        url = "https://fofa.info/result?qbase64=" + qb64 + "&page=" + str(page) + "&page_size=50"
        html = subprocess.run(["curl", "-sk", "--connect-timeout", "10", "--max-time", "20", url],
                             capture_output=True, text=True).stdout
        
        for m in re.finditer(r'target="_blank">\s*([a-z0-9.-]+\.[a-z]{2,})\s*<', html, re.I):
            d = m.group(1).strip().lower()
            if len(d) > 5 and '.' in d:
                all_domains.add(d)
        
        # Also try the span/div element format
        for m in re.finditer(r'<span[^>]*>([a-z0-9.-]+\.[a-z]{2,})</span>', html, re.I):
            d = m.group(1).strip().lower()
            if len(d) > 5 and '.' in d:
                all_domains.add(d)
        
        time.sleep(2)
    
    return all_domains

# ====== 搜索列表 ======
SEARCHES = [
    ("PHP5.2", 'header="PHP/5.2"'),
    ("PHP5.3", 'header="PHP/5.3"'),
    ("PHP5.4", 'header="PHP/5.4"'),
    ("DedeCMS", 'app="DedeCMS"'),
    ("ThinkPHP", 'header="ThinkPHP"'),
    ("IIS6-Win2003", 'server="Microsoft-IIS/6.0"'),
    ("IIS7.5", 'server="Microsoft-IIS/7.5"'),
    ("ASP.NET", 'header="ASP.NET"'),
    ("Apache2.2+PHP5", 'server="Apache/2.2" && header="PHP/5."'),
]

all_found = set()

for name, query in SEARCHES:
    try:
        domains = fofa_search(query, pages=2)
        print(name + ": " + str(len(domains)) + " domains")
        all_found.update(domains)
    except Exception as e:
        print(name + ": FAILED - " + str(e))

# 保存
with open("/tmp/old_targets.txt", "w") as f:
    for d in sorted(all_found):
        f.write(d + "\n")

print("\nTotal unique: " + str(len(all_found)))
print("Saved: /tmp/old_targets.txt")

for d in sorted(all_found)[:30]:
    print("  " + d)
