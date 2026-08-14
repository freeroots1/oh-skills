#!/usr/bin/env python3
"""sonear.fit 单次登录测试"""
import urllib.request, http.cookiejar, ssl, sys, time
import ddddocr

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B = "http://sonear.fit"
ocr = ddddocr.DdddOcr(show_ad=False)

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]

# 多次尝试打印验证码识别结果和响应
for i in range(8):
    cap = op.open(f"{B}/login/captcha", timeout=8).read()
    code = ocr.classification(cap)
    print(f"[{i}] 验证码={code} (len={len(code)})", flush=True)
    if len(code) != 4:
        continue
    data = f"username=admin&password=admin123&captchaInput={code}".encode()
    try:
        r = op.open(urllib.request.Request(f"{B}/login/doLogin?returnUrl=", data=data), timeout=8)
        body = r.read().decode("utf-8","ignore")
        print(f"  响应: len={len(body)} url={r.geturl()}", flush=True)
        print(f"  内容: {body[:200]}", flush=True)
    except Exception as e:
        print(f"  ERR: {str(e)[:60]}", flush=True)
    time.sleep(0.5)
