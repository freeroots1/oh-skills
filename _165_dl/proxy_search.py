#!/usr/bin/env python3
"""代理+搜索引擎采集网站"""
import subprocess, re, time, random, urllib.parse

with open("/tmp/working_proxies.txt") as f:
    PROXIES = [l.strip() for l in f if l.strip()]

KEYWORDS = [
    "公司 inurl:asp site:cn",
    "有限公司 inurl:asp site:com.cn",
    "企业 inurl:aspx site:cn",
    "公司 inurl:?id= site:cn",
    "有限公司 inurl:?catid= site:com.cn",
    "企业 inurl:?page= site:cn",
    "产品 inurl:?productid= site:cn",
    '"Powered by DedeCMS" 公司 site:cn',
    '"Powered by DedeCMS" 有限公司 site:com.cn',
    'inurl:/dede/ 公司 site:cn',
    '"Powered by EmpireCMS" 公司 site:cn',
    '"Powered by 动易" 公司 site:cn',
    '"动易" inurl:asp site:cn',
    "intitle:Index of / 公司 site:cn",
    "Fatal error 公司 site:cn",
    "Warning: mysql_connect 公司 site:cn",
    "化工 inurl:asp site:cn",
    "机械 inurl:aspx site:cn",
    "教育 inurl:php?id= site:cn",
    "inurl:admin 公司 site:cn",
    "intitle:后台管理 公司 site:cn",
    "公司 inurl:asp site:net.cn",
]

all_domains = set()
SKIP = ["bing", "microsoft", "google", "github", "csdn", "baidu", "zhihu", "tencent", "php.net", "w3schools"]

def search(q):
    p = random.choice(PROXIES)
    encoded = urllib.parse.quote(q)
    url = "https://cn.bing.com/search?q=" + encoded + "&count=10"
    try:
        r = subprocess.run(["curl", "-sk", "--connect-timeout", "8", "--max-time", "15",
                           "-x", "http://" + p,
                           "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                           url], capture_output=True, text=True, timeout=20)
        for m in re.finditer(r"https?://([a-z0-9.-]+\.[a-z]{2,})", r.stdout):
            dom = m.group(1).lower()
            if not any(s in dom for s in SKIP) and len(dom) > 7:
                all_domains.add(dom)
    except:
        pass

for i, kw in enumerate(KEYWORDS):
    print("[%d/%d] %s" % (i+1, len(KEYWORDS), kw[:50]))
    search(kw)
    time.sleep(random.uniform(2, 5))

with open("/tmp/proxy_collected.txt", "w") as f:
    for d in sorted(all_domains):
        f.write(d + "\n")

print("\nTotal: %d domains" % len(all_domains))
for d in sorted(all_domains)[:25]:
    print("  " + d)
