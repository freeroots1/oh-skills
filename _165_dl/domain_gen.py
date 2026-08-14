import socket, subprocess, threading, sys

# 中国常见企业命名模式
cities = ['beijing','shanghai','tianjin','chongqing','guangzhou','shenzhen',
    'hangzhou','nanjing','wuhan','chengdu','suzhou','qingdao','dalian','xiamen',
    'ningbo','zhuhai','dongguan','foshan','shenyang','zhengzhou','changsha',
    'hefei','kunming','nanning','xian','fuzhou','wuxi','changzhou','wenzhou',
    'jinan','haikou','guiyang','lanzhou','taiyuan','haerbin','changchun',
    'wulumuqi','nanchang','guiyang']

biz = ['jixie','gongcheng','jianzhu','jiancai','dianqi','dianji','dianlan',
    'zhoucheng','gangtie','yeya','qizhong','jingmi','muju','zhugang',
    'gangjiegou','wujin','bengfa','shukong','jidian','jichuang','bianyaqi',
    'yibiao','tongyong','zidonghua','diangong','dianhan','fengji','jianyan',
    'shebei','zhizao','jinchukou','shiyou','huagong','huanbao','nengyuan',
    'guangdian','tongxin','ruanjian','wangluo','wuliu','baozhuang',
    'mucai','shipin','yiliao','zhongyi','fangzhi','fushi','wujin']

suffixes = ['.com', '.com.cn', '.cn']

found = []
lock = threading.Lock()
tested = [0]
MAX = 300  # limit results

def check(domain):
    try:
        ip = socket.gethostbyname(domain)
        if ip:
            with lock:
                tested[0] += 1
            try:
                r = subprocess.run(
                    ['curl', '-sk', '--connect-timeout', '3', '--max-time', '5',
                     'http://' + domain, '-o', '/dev/null', '-w',
                     '%{http_code}|%{size_download}|%{server}'],
                    capture_output=True, text=True, timeout=6)
                parts = r.stdout.strip().split('|')
                code = parts[0] if len(parts) > 0 else '000'
                size = parts[1] if len(parts) > 1 else '0'
                server = parts[2] if len(parts) > 2 else ''
                
                # Only keep real sites (200+, not micro/small)
                if code in ['200','301','302'] and int(size) > 2000:
                    with lock:
                        found.append(domain)
                        print(domain + ' [' + ip + '] ' + code + ':' + size + 'B ' + server[:30])
            except:
                pass
    except:
        pass

threads = []
for city in cities:
    for b in biz:
        if len(found) >= MAX:
            break
        for suffix in suffixes:
            domain = city + b + suffix
            t = threading.Thread(target=check, args=(domain,))
            t.start()
            threads.append(t)
    if len(found) >= MAX:
        break

for t in threads:
    t.join(3)

print('Found:', len(found), 'Tested:', tested[0])
