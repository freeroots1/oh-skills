#!/usr/bin/env python3
"""Redis未授权批量扫描"""
import socket

def check(ip, t=2):
    try:
        s = socket.socket(); s.settimeout(t)
        s.connect((ip, 6379))
        s.send(b"PING\r\n")
        r = s.recv(50)
        s.close()
        return b"PONG" in r
    except: return False

ips = [l.strip() for l in open("/tmp/redis_ips.txt") if l.strip()]
print(f"扫描 {len(ips)} IP", flush=True)
hits = []
for i, ip in enumerate(ips):
    if check(ip):
        print(f"[REDIS-NO-AUTH] {ip}", flush=True)
        hits.append(ip)
    if i % 100 == 0:
        print(f"...{i}/{len(ips)}", flush=True)
print(f"DONE: {len(hits)} hits", flush=True)
with open("/tmp/redis_hits.txt", "w") as f:
    f.write("\n".join(hits))
