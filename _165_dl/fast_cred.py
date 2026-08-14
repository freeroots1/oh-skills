#!/usr/bin/env python3
"""Fast credential testing - FTP, MySQL, Redis only."""
import subprocess, socket, re, sys

open_ports = {}
with open('/tmp/nmap_results.gnmap') as f:
    for line in f:
        if line.startswith('#') or 'open' not in line.lower(): continue
        parts = line.strip().split()
        ip = parts[1]
        open_ports[ip] = []
        for part in parts[2:]:
            m = re.match(r'(\d+)/open', part)
            if m: open_ports[ip].append(int(m.group(1)))

PASSWORDS = ['', 'root', 'admin', '123456', 'password', 'mysql']

def try_mysql(ip, port):
    for pw in PASSWORDS:
        try:
            pw_arg = f"-p'{pw}'" if pw else ''
            r = subprocess.run(
                f"timeout 4 mysql -h {ip} -P {port} -u root {pw_arg} --connect-timeout=2 -e 'SELECT 1' 2>/dev/null",
                shell=True, capture_output=True, text=True, timeout=6)
            if '1' in r.stdout:
                return f"MySQL root:{pw if pw else '(empty)'}"
        except:
            pass
    return None

def try_ftp(ip, port):
    creds = [('anonymous','anonymous'), ('ftp','ftp'), ('admin','admin'), ('test','test')]
    for user, pw in creds:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((ip, port))
            s.recv(1024)
            s.send(f'USER {user}\r\n'.encode())
            s.recv(1024)
            s.send(f'PASS {pw}\r\n'.encode())
            resp = s.recv(1024).decode(errors='ignore')
            s.close()
            if '230' in resp:
                return f"FTP {user}:{pw}"
        except:
            pass
    return None

def try_redis(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        s.connect((ip, port))
        s.send(b'PING\r\n')
        resp = s.recv(1024).decode(errors='ignore')
        s.close()
        if 'PONG' in resp:
            return 'Redis (no auth)'
    except:
        pass
    return None

results = []
for ip in sorted(open_ports):
    ports = open_ports[ip]
    for port in ports:
        r = None
        if port == 3306:
            r = try_mysql(ip, port)
        elif port == 21:
            r = try_ftp(ip, port)
        elif port == 6379:
            r = try_redis(ip, port)
        if r:
            results.append((ip, port, r))
            print(f'SUCCESS: {ip}:{port} - {r}', flush=True)

print()
print('=' * 50)
print(f'Total credential successes: {len(results)}')
for ip, port, cred in results:
    print(f'  {ip}:{port} - {cred}')
