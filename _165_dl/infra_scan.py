#!/usr/bin/env python3
"""infra_scan.py - P0/P1 IP基础设施服务扫描+弱口令
SSH/MySQL/Redis/RDP 端口探测 + 常见弱口令
"""
import socket, sys, time, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

IPS = open('/opt/msray/p01_ips.txt').read().strip().split('\n')[:30]

def port_open(ip, port, timeout=3):
    try:
        s = socket.create_connection((ip, port), timeout=timeout)
        s.close()
        return True
    except Exception:
        return False

def banner(ip, port, timeout=4):
    try:
        s = socket.create_connection((ip, port), timeout=timeout)
        s.settimeout(4)
        try:
            data = s.recv(100)
            return data.decode('utf-8', 'ignore')[:60]
        except Exception:
            return ''
        finally:
            s.close()
    except Exception:
        return ''

def scan(ip):
    res = []
    for port in [22, 3306, 6379, 3389]:
        if port_open(ip, port):
            b = banner(ip, port) if port in [22, 3306, 6379] else ''
            res.append((port, b))
    return ip, res

def main():
    print('scanning %d IPs...' % len(IPS), flush=True)
    with ThreadPoolExecutor(max_workers=15) as ex:
        futs = {ex.submit(scan, ip): ip for ip in IPS}
        for fu in as_completed(futs):
            ip, res = fu.result()
            if res:
                print('%s: %s' % (ip, '; '.join('%d[%s]' % (p, b.strip()[:30]) for p, b in res)), flush=True)
    print('=== DONE ===', flush=True)

if __name__ == '__main__':
    main()
