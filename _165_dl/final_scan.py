import socket, subprocess, threading, sys

# 大量新段
ranges = []
for i in range(200, 215): ranges.append(f'121.196.{i}.')
for i in range(220, 240): ranges.append(f'121.196.{i}.')
for i in range(40, 46): ranges.append(f'121.40.{i}.')
for i in range(30, 36): ranges.append(f'121.42.{i}.')
for i in range(40, 46): ranges.append(f'121.43.{i}.')
for i in range(70, 82): ranges.append(f'120.76.{i}.')
for i in range(100, 112): ranges.append(f'47.104.{i}.')
for i in range(240, 255): ranges.append(f'47.88.{i}.')
for i in range(86, 100): ranges.append(f'8.210.{i}.')

print(f'Scanning {len(ranges)} subnets...')

hits = []
lock = threading.Lock()
found = [0]
MAX = 30

def probe(ip):
    try:
        s = socket.socket(); s.settimeout(0.3)
        if s.connect_ex((ip, 80)) == 0:
            s.close()
            r = subprocess.run(['curl','-sk','--connect-timeout','2','--max-time','2',
                f'http://{ip}','-o','/dev/null','-w','%{http_code}|%{size_download}'],
                capture_output=True,text=True,timeout=3)
            p = r.stdout.strip().split('|')
            if p[0] in ('200','301','302','403') and len(p) > 1 and int(p[1]) > 500:
                rdp = False
                try:
                    s2 = socket.socket(); s2.settimeout(0.3)
                    rdp = s2.connect_ex((ip, 3389)) == 0; s2.close()
                except: pass
                with lock:
                    tag = 'RDP' if rdp else ''
                    hits.append(f'{ip} [{tag}] {p[1]}B')
                    found[0] += 1
                    if rdp or int(p[1]) > 10000:
                        print(f'{ip} [{tag}] {p[1]}B')
    except: pass

threads = []
for subnet in ranges:
    for host in range(1, 12):
        if found[0] >= MAX: break
        t = threading.Thread(target=probe, args=(subnet+str(host),))
        t.start(); threads.append(t)
    if found[0] >= MAX: break

for t in threads: t.join(3)

print(f'\nTotal: {len(hits)}')
for x in hits: print(f'  {x}')
