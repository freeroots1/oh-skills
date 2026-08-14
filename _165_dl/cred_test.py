#!/usr/bin/env python3
"""Passive credential testing - common defaults only, no brute force."""
import subprocess, socket, time, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Parse nmap grepable output
open_ports = {}  # ip -> [ports]
with open('/tmp/nmap_results.gnmap') as f:
    for line in f:
        if line.startswith('#') or 'open' not in line.lower():
            continue
        parts = line.strip().split()
        ip = parts[1]
        open_ports[ip] = []
        for part in parts[2:]:
            m = re.match(r'(\d+)/open', part)
            if m:
                open_ports[ip].append(int(m.group(1)))

print(f"Total IPs with open ports: {len(open_ports)}")
results = []

def try_ssh(ip, port):
    creds = ['root:root', 'root:admin', 'root:toor', 'root:123456', 'root:password',
             'admin:admin', 'admin:123456', 'test:test']
    for cred in creds:
        user, passwd = cred.split(':', 1)
        try:
            # Using sshpass if available
            cmd = f"timeout 8 sshpass -p '{passwd}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=4 -o PreferredAuthentications=password -o BatchMode=no {user}@{ip} -p {port} 'echo SUCCESS'"
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=12)
            if 'SUCCESS' in r.stdout:
                return f"SSH SUCCESS {ip}:{port} {user}:{passwd}"
        except:
            pass
    return None

def try_ftp(ip, port):
    creds = ['anonymous:anonymous', 'ftp:ftp', 'admin:admin', 'test:test', 'ftp:ftp@']
    for cred in creds:
        user, passwd = cred.split(':', 1)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(8)
            sock.connect((ip, port))
            banner = sock.recv(1024).decode(errors='ignore')
            sock.send(f'USER {user}\r\n'.encode())
            resp1 = sock.recv(1024).decode(errors='ignore')
            sock.send(f'PASS {passwd}\r\n'.encode())
            resp2 = sock.recv(1024).decode(errors='ignore')
            sock.close()
            if '230' in resp2:
                return f"FTP SUCCESS {ip}:{port} {user}:{passwd}"
        except:
            pass
    return None

def try_mysql(ip, port):
    passwords = ['', 'root', 'admin', '123456', 'password', 'mysql', 'root123']
    for passwd in passwords:
        try:
            if passwd:
                cmd = f"timeout 8 mysql -h {ip} -P {port} -u root -p'{passwd}' --connect-timeout=4 -e 'SELECT 1' 2>/dev/null"
            else:
                cmd = f"timeout 8 mysql -h {ip} -P {port} -u root --connect-timeout=4 -e 'SELECT 1' 2>/dev/null"
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=12)
            if '1' in r.stdout:
                return f"MySQL SUCCESS {ip}:{port} root:{passwd if passwd else '(empty)'}"
        except:
            pass
    return None

def try_redis(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(8)
        sock.connect((ip, port))
        sock.send(b'PING\r\n')
        resp = sock.recv(1024).decode(errors='ignore')
        sock.close()
        if 'PONG' in resp:
            # Try to get info
            sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock2.settimeout(8)
            sock2.connect((ip, port))
            sock2.send(b'INFO\r\n')
            info = sock2.recv(2048).decode(errors='ignore')
            sock2.close()
            return f"Redis SUCCESS (no auth) {ip}:{port}"
    except:
        pass
    return None

def try_mssql(ip, port):
    # Basic TDS probe - just note
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((ip, port))
        sock.close()
        return f"MSSQL OPEN {ip}:{port} (cred test needs specialized tool)"
    except:
        pass
    return None

def process_ip(ip, ports):
    ip_results = []
    for port in ports:
        result = None
        if port == 22:
            result = try_ssh(ip, port)
        elif port == 21:
            result = try_ftp(ip, port)
        elif port == 3306:
            result = try_mysql(ip, port)
        elif port == 6379:
            result = try_redis(ip, port)
        elif port == 1433:
            result = try_mssql(ip, port)
        elif port in [3389, 5985, 8080, 8443]:
            # RDP/WinRM/HTTP - just note
            result = f"PORT OPEN {ip}:{port} (passive test not applicable)"
        
        if result:
            ip_results.append(result)
            print(f"  [+] {result}")
        elif port in [22, 21, 3306, 6379]:
            print(f"  [-] {ip}:{port} - no default creds worked")
    
    return ip_results

# Process all IPs - sequentially to be gentle
all_results = []
for ip, ports in sorted(open_ports.items()):
    print(f"\n[*] Testing {ip} (ports: {ports})")
    ip_results = process_ip(ip, ports)
    all_results.extend(ip_results)

print("\n" + "="*60)
print("CREDENTIAL TEST RESULTS SUMMARY")
print("="*60)
for r in all_results:
    print(f"  {r}")

# Write detailed output
with open('/tmp/cred_results.txt', 'w') as f:
    f.write("=== CREDENTIAL TEST RESULTS ===\n\n")
    for r in all_results:
        f.write(r + "\n")
    f.write(f"\nTotal findings: {len(all_results)}\n")

print(f"\nTotal findings: {len(all_results)}")
print("Results written to /tmp/cred_results.txt")
