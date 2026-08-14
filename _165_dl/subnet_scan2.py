#!/usr/bin/env python3
import socket, subprocess, threading

print('Scanning 121.196.233.0/24...')
live = []
lock = threading.Lock()

def check(ip):
    try:
        s = socket.socket(); s.settimeout(0.5)
        if s.connect_ex((ip, 80)) == 0:
            s.close()
            r = subprocess.run(['curl','-sk','--connect-timeout','2','--max-time','3',
                f'http://{ip}','-o','/dev/null','-w','%{http_code}:%{size_download}:%{server}'],
                capture_output=True,text=True,timeout=4)
            parts = r.stdout.strip().split(':',2)
            if parts[0] in ['200','301','302','403'] and int(parts[1]) > 50:
                with lock:
                    live.append((ip, parts[0], int(parts[1]), parts[2] if len(parts)>2 else '?'))
                    print(f'{ip} [{parts[0]}] {parts[1]}B {parts[2][:30] if len(parts)>2 else "?"}')
    except: pass

threads = []
for i in range(1, 50):
    t = threading.Thread(target=check, args=(f'121.196.233.{i}',))
    t.start(); threads.append(t)
for t in threads: t.join(5)

print(f'Live: {len(live)}')
for ip, code, size, server in live:
    print(f'  {ip}  {code}  {size}B  {server}')
