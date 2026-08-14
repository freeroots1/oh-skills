import socket, subprocess

# 中国主要城市全拼
cities = ['beijing','shanghai','tianjin','chongqing','guangzhou','shenzhen',
    'hangzhou','nanjing','wuhan','chengdu','suzhou','wuxi','ningbo','dongguan',
    'foshan','zhengzhou','changsha','qingdao','dalian','jinan','xian','hefei',
    'fuzhou','xiamen','kunming','nanning','shenyang','changchun','haerbin',
    'shijiazhuang','taiyuan','guiyang','lanzhou','wulumuqi','nanchang',
    'wenzhou','jiaxing','jinhua','taizhou','yantai','weifang','luoyang',
    'tangshan','baoding','handan']

# 行业关键词
biz = ['jixie','jidian','dianji','dianqi','dianlan','zhoucheng','gangtie',
    'jianzhu','jiancai','gongcheng','yeya','qizhong','jingmi','muju',
    'zhugang','gangjiegou','bianyaqi','jichuang','wujin','bengfa',
    'shukong','muju','zhizao','shebei','yibiao','tongyong','zidonghua',
    'diangong','dianhan','fengji','jianyan','ceshi','jingji']

# 后缀
suffixes = ['.com','.com.cn','.cn']

results = []
for c in cities:
    for b in biz:
        dom = c + b + '.com'
        try:
            ip = socket.gethostbyname(dom)
            r = subprocess.run(['curl','-sk','--connect-timeout','2','--max-time','3',
                'http://'+dom,'-o','/dev/null','-w','%{http_code}:%{size_download}'],
                capture_output=True,text=True,timeout=4)
            code_size = r.stdout.strip()
            if not code_size.startswith('000'):
                print(dom + ' [' + ip + '] ' + code_size)
                results.append(dom)
            if len(results) >= 20:
                break
        except:
            pass
    if len(results) >= 20:
        break

print('Found:', len(results))
