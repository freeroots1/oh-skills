import socket, subprocess, threading

# 阿里云全量国内段
ranges = []
# 华东1 杭州
for i in range(40, 44): ranges.append(f'121.43.{i}.')
for i in range(196, 200): ranges.append(f'121.196.{i}.')
for i in range(232, 240): ranges.append(f'121.196.{i}.')
# 华东2 上海
for i in range(24, 30): ranges.append(f'120.25.{i}.')
for i in range(55, 61): ranges.append(f'120.55.{i}.')
# 华北1青岛/北京
for i in range(88, 100): ranges.append(f'47.95.{i}.')
for i in range(104, 112): ranges.append(f'47.104.{i}.')
# 华南1深圳
for i in range(76, 81): ranges.append(f'120.76.{i}.')
# 香港
for i in range(74, 80): ranges.append(f'47.74.{i}.')
for i in range(89, 93): ranges.append(f'47.89.{i}.')
for i in range(95, 99): ranges.append(f'8.215.{i}.')
# 新加坡
for i in range(210, 216): ranges.append(f'47.88.{i}.')
# 西南1 成都
for i in range(98, 103): ranges.append(f'47.98.{i}.')
# 其他
for i in range(56, 60): ranges.append(f'123.56.{i}.')
for i in range(124, 127): ranges.append(f'112.124.{i}.')

print(f'Scanning {len(ranges)} subnets...')

iis_rdp = []
lock = threading.Lock()
found = [0]

def probe(ip):
    try:
        s = socket.socket(); s.settimeout(0.4)
        if s.connect_ex((ip, 80)) == 0:
            s.close()
            r = subprocess.run(['curl','-sk','--connect-timeout','2','--max-time','2',
                f'http://{ip}','-D','-','-o','/dev/null'],
                capture_output=True,text=True,timeout=3)
            out = r.stdout
            if 'IIS' in out or 'Microsoft' in out:
                rdp = False
                try:
                    s2 = socket.socket(); s2.settimeout(0.4)
                    rdp = s2.connect_ex((ip, 3389)) == 0; s2.close()
                except: pass
                tag = 'RDP' if rdp else 'IIS'
                with lock:
                    iis_rdp.append(f'{ip} [{tag}]')
                    found[0] += 1
                    print(f'{ip} [{tag}]')
    except: pass

threads = []
for subnet in ranges:
    for host in range(1, 11):
        if found[0] >= 25: break
        t = threading.Thread(target=probe, args=(subnet+str(host),))
        t.start(); threads.append(t)
    if found[0] >= 25: break

for t in threads: t.join(3)

print(f'\nTotal IIS: {len(iis_rdp)}')
for x in iis_rdp: print(f'  {x}')
