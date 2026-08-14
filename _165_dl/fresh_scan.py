import socket, subprocess, threading

# 阿里云高价值段 + 相邻段
ranges = []
for i in range(232, 240): ranges.append(f'121.196.{i}.')  # 相邻段
for i in range(196, 200): ranges.append(f'121.40.{i}.')   # 上海
for i in range(40, 44): ranges.append(f'121.43.{i}.')      # 杭州
for i in range(88, 96): ranges.append(f'47.95.{i}.')       # 新加坡/香港

hits = []
lock = threading.Lock()

def probe(ip):
    try:
        s = socket.socket(); s.settimeout(0.6)
        if s.connect_ex((ip, 80)) == 0:
            s.close()
            r = subprocess.run(['curl','-sk','--connect-timeout','2','--max-time','3',
                f'http://{ip}','-o','/dev/null','-w','%{http_code}|%{size_download}|%{server}'],
                capture_output=True,text=True,timeout=4)
            p = r.stdout.strip().split('|',2)
            if p[0] in ('200','301','302','403') and len(p) > 1 and int(p[1]) > 500:
                sv = p[2][:30] if len(p) > 2 else '?'
                # Check for IIS/Windows
                is_iis = 'IIS' in sv or 'Microsoft' in sv
                # Check RDP
                rdp = False
                try:
                    s2 = socket.socket(); s2.settimeout(0.5)
                    rdp = s2.connect_ex((ip, 3389)) == 0; s2.close()
                except: pass
                with lock:
                    hits.append((ip, p[1], sv, is_iis, rdp))
                    tag = 'IIS+RDP' if (is_iis and rdp) else 'RDP' if rdp else 'IIS' if is_iis else ''
                    if tag:
                        print(f'!!! {ip} [{tag}] {p[1]}B {sv}')
                    elif int(p[1]) > 10000:
                        print(f'{ip} [{p[0]}] {p[1]}B {sv}')
    except: pass

threads = []
count = 0
for subnet in ranges:
    for host in range(1, 15):
        t = threading.Thread(target=probe, args=(subnet+str(host),))
        t.start(); threads.append(t)

for t in threads: t.join(4)

iis_rdp = [(ip,sz,sv) for ip,sz,sv,iis,rdp in hits if iis and rdp]
rdp = [(ip,sz,sv) for ip,sz,sv,iis,rdp in hits if rdp and not iis]
big = [(ip,sz,sv) for ip,sz,sv,iis,rdp in hits if not iis and not rdp and int(sz) > 10000]

print(f'\nIIS+RDP: {len(iis_rdp)}, RDP: {len(rdp)}, Big(>10KB): {len(big)}, Total: {len(hits)}')
