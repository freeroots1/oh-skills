import socket, subprocess, threading

# 阿里云常用企业站IP段(国内)
ranges = [
    '121.196.233.',  # 货车记账本所在段
    '118.190.207.',  # wanzhengdq所在段  
    '120.79.41.',    # 农批友所在段
    '117.50.115.',   # 高价值段
    '113.113.81.',   # silverplus段
    '123.57.180.',   # 另一高价值段
    '101.126.76.',   # 
    '106.53.203.',
    '180.76.145.',
    '154.89.238.',
]

found = []
lock = threading.Lock()

def check_ip(ip):
    try:
        s = socket.socket()
        s.settimeout(1)
        if s.connect_ex((ip, 80)) == 0:
            s.close()
            r = subprocess.run(
                ['curl', '-sk', '--connect-timeout', '3', '--max-time', '4',
                 'http://' + ip, '-o', '/dev/null', '-w',
                 '%{http_code}|%{size_download}|%{server}'],
                capture_output=True, text=True, timeout=5)
            out = r.stdout.strip()
            parts = out.split('|')
            code = parts[0] if len(parts) > 0 else '000'
            if code in ['200', '301', '302', '403']:
                server = parts[2] if len(parts) > 2 else ''
                size = parts[1] if len(parts) > 1 else '0'
                with lock:
                    print(ip + ' [' + server + '] ' + code + ':' + size)
                    found.append(ip)
    except:
        pass

threads = []
for subnet in ranges:
    for host in range(1, 50):
        if len(found) >= 20:
            break
        ip = subnet + str(host)
        t = threading.Thread(target=check_ip, args=(ip,))
        t.start()
        threads.append(t)

for t in threads:
    t.join(3)

print('Found:', len(found))
