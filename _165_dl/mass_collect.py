#!/usr/bin/env python3
"""全行业域名批量采集——不限行业,只要.cn/.com.cn企业站"""
import subprocess, json, socket, threading, time

domains = set()

# ============== 方法1: CommonCrawl 多索引 ==============
print('[1] CommonCrawl...')
indexes = ['CC-MAIN-2024-30','CC-MAIN-2024-22','CC-MAIN-2024-10','CC-MAIN-2023-50']
for idx in indexes:
    CC = f'https://index.commoncrawl.org/{idx}-index'
    queries = [
        'url=*.com.cn/*&filter=status:200&output=json&limit=200',
        'url=*.cn/*&filter=status:200&output=json&limit=100',
        'url=*/news.asp*&filter=status:200&output=json&limit=30',
        'url=*/products.asp*&filter=status:200&output=json&limit=30',
        'url=*/about.asp*&filter=status:200&output=json&limit=30',
    ]
    for q in queries:
        try:
            r = subprocess.run(['curl','-sk','--connect-timeout','15',f'{CC}?{q}'],
                capture_output=True,text=True,timeout=20)
            for line in r.stdout.strip().split('\n'):
                if not line: continue
                try:
                    d = json.loads(line)
                    import re
                    m = re.search(r'https?://([^/]+)', d.get('url',''))
                    if m: domains.add(m.group(1))
                except: pass
        except: pass

# ============== 方法2: DNS全城市全行业生成 ==============
print(f'[2] DNS生成 ({len(domains)} collected)...')
cities = ['beijing','shanghai','tianjin','chongqing','guangzhou','shenzhen','hangzhou',
    'nanjing','wuhan','chengdu','qingdao','dalian','xiamen','suzhou','wuxi','fuzhou',
    'ningbo','changsha','zhengzhou','hefei','xian','kunming','shenyang','haerbin',
    'nanchang','guiyang','lanzhou','taiyuan','nanning','wenzhou','dongguan','foshan',
    'zhuhai','jinan','haikou','wulumuqi','hohhot','lasa','yinchuan','xining']

biz = ['jixie','gongcheng','jianzhu','dianqi','dianlan','zhoucheng','gangtie','yeya',
    'jingmi','wujin','jiancai','dianji','yibiao','jichuang','zhugang','shukong',
    'huagong','fangzhi','shipin','yiliao','zhongyi','baozhuang','mucai','wuliu',
    'huanbao','nengyuan','tongxin','ruanjian','dianzi','guangdian','jinshu','suliao',
    'gangjiegou','bengfa','bianyaqi','shengjiang','tongfeng','paishui','gongre',
    'zhileng','kongtiao','jiadian','qiche','mopei','muju','zhizao','jiagong',
    'zidonghua','jidian','shebei','yiqi','shiyou','tianranqi','meitan','kuangye',
    'dianhan','tuliao','xiangjiao','boli','taoci','ditan','menshi','jiaju',
    'zhaoming','ledeng','taiyangneng','fengdian','shuili','zaochuan','hangkong']

found_dns = [0]
lock = threading.Lock()

def check_dns(domain):
    try:
        ip = socket.gethostbyname(domain)
        if ip:
            with lock:
                domains.add(domain)
                found_dns[0] += 1
    except: pass

threads = []
for c in cities:
    for b in biz:
        if found_dns[0] >= 100: break
        for ext in ['.com','.com.cn','.cn','.net']:
            t = threading.Thread(target=check_dns, args=(c+b+ext,))
            t.start(); threads.append(t)

for t in threads: t.join(5)

# ============== 保存 ==============
print(f'[3] Total: {len(domains)} domains')
with open('/tmp/mass_targets.txt','w') as f:
    for d in sorted(domains):
        f.write(d + '\n')
print('Saved to /tmp/mass_targets.txt')
