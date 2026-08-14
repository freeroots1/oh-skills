#!/usr/bin/env python3
"""
========================================
  全自动域名采集工具箱 v1.0
  — 无需人工,一键收集企业域名
========================================
用法: python 全自动采集器.py [方法编号]

方法:
  1 = CommonCrawl API (免费,全球索引)
  2 = DNS批量生成 (城市+行业拼音)
  3 = 阿里云IP段扫描 (找Windows服务器)
  4 = 全部运行
"""

import re, sys, json, socket, subprocess, threading, time

# ============================================
# 方法1: CommonCrawl API
# ============================================
def method_commoncrawl():
    print("[1/4] CommonCrawl CDX API...")
    CC = "https://index.commoncrawl.org/CC-MAIN-2024-30-index"
    domains = set()
    
    queries = [
        ('url=*.com.cn/*&filter=status:200&output=json&limit=100', 'com.cn企业'),
        ('url=*.cn/*&filter=encoding:gb2312&output=json&limit=50', 'GB2312老站'),
        ('url=*/news.asp*&filter=status:200&output=json&limit=50', 'ASP新闻页'),
        ('url=*/products.asp*&filter=status:200&output=json&limit=50', 'ASP产品页'),
    ]
    
    for q, desc in queries:
        try:
            r = subprocess.run(['curl','-sk','--connect-timeout','20',f'{CC}?{q}'],
                capture_output=True,text=True,timeout=25)
            count = 0
            for line in r.stdout.strip().split('\n'):
                if not line: continue
                try:
                    d = json.loads(line)
                    m = re.search(r'https?://([^/]+)', d.get('url',''))
                    if m: domains.add(m.group(1)); count += 1
                except: pass
            print(f"  {desc}: +{count} 域名")
        except: pass
    
    return domains

# ============================================
# 方法2: DNS批量生成
# ============================================
def method_dns_generate():
    print("[2/4] DNS域名生成...")
    cities = ['beijing','shanghai','tianjin','guangzhou','shenzhen','hangzhou',
        'nanjing','wuhan','chengdu','qingdao','dalian','xiamen','suzhou','wuxi',
        'fuzhou','changsha','zhengzhou','hefei','xian','kunming','shenyang','ningbo']
    biz = ['jixie','gongcheng','jianzhu','dianqi','dianlan','zhoucheng','gangtie',
        'yeya','jingmi','jidian','wujin','jiancai','dianji','yibiao','jichuang',
        'zhugang','gangjiegou','shukong','bengfa','diangong']
    
    domains = set()
    found = [0]
    lock = threading.Lock()
    
    def check(domain):
        try:
            ip = socket.gethostbyname(domain)
            if ip:
                with lock:
                    domains.add(domain)
                    found[0] += 1
        except: pass
    
    threads = []
    for c in cities:
        for b in biz:
            if found[0] >= 50: break
            for ext in ['.com','.com.cn','.cn']:
                t = threading.Thread(target=check, args=(c+b+ext,))
                threads.append(t); t.start()
    
    for t in threads: t.join(5)
    print(f"  DNS生成: {len(domains)} 域名")
    return domains

# ============================================
# 方法3: 阿里云IP扫描(IIS+Microsoft)
# ============================================
def method_alicloud_scan():
    print("[3/4] 阿里云IP扫描...")
    ranges = []
    for i in range(88, 120): ranges.append(f'47.{i}.')  # 47.x
    for i in range(24, 36): ranges.append(f'120.{i}.')  # 120.x
    for i in range(40, 43): ranges.append(f'121.{i}.')  # 121.x
    for i in range(196, 200): ranges.append(f'121.{i}.')
    for i in range(190, 192): ranges.append(f'118.{i}.') # 118.x
    
    iis_found = []
    lock = threading.Lock()
    
    def check(ip):
        try:
            s = socket.socket(); s.settimeout(0.5)
            if s.connect_ex((ip, 80)) == 0:
                s.close()
                r = subprocess.run(['curl','-sk','--connect-timeout','2','--max-time','3',
                    f'http://{ip}','-D','-','-o','/dev/null'],
                    capture_output=True,text=True,timeout=4)
                if 'IIS' in r.stdout or 'Microsoft' in r.stdout:
                    with lock:
                        iis_found.append(ip)
                        print(f"  IIS: {ip}")
        except: pass
    
    threads = []
    for subnet in ranges:
        for host in range(1, 6):
            if len(iis_found) >= 20: break
            t = threading.Thread(target=check, args=(subnet+str(host),))
            threads.append(t); t.start()
    
    for t in threads: t.join(5)
    print(f"  IIS服务器: {len(iis_found)} 台")
    return set(f'IP_{ip}' for ip in iis_found)

# ============================================
# 主程序
# ============================================
def main():
    method = sys.argv[1] if len(sys.argv) > 1 else '4'
    
    all_domains = set()
    
    if method in ('1', '4'): all_domains.update(method_commoncrawl())
    if method in ('2', '4'): all_domains.update(method_dns_generate())
    if method in ('3', '4'): all_domains.update(method_alicloud_scan())
    
    # 去重保存
    outfile = '/tmp/collected_domains.txt'
    with open(outfile, 'w') as f:
        for d in sorted(all_domains):
            f.write(d + '\n')
    
    print(f"\n✅ 总计采集: {len(all_domains)} 个域名")
    print(f"✅ 已保存: {outfile}")

if __name__ == '__main__':
    main()
