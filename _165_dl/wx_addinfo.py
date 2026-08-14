#!/usr/bin/env python3
"""wxiajin 信息发布上传探测"""
import urllib.request, http.cookiejar, urllib.parse, ssl, re

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "https://wxiajin.com"

r = op.open(f"{B}/e/member/login/", timeout=10); r.read()
data = urllib.parse.urlencode({"enews":"login","username":"hunter888","password":"hunter123"}).encode()
req = urllib.request.Request(f"{B}/e/member/doaction.php", data=data, headers={"Referer":f"{B}/e/member/login/"})
r = op.open(req, timeout=10); r.read()

# 信息发布-添加信息
for p in ["/e/DoInfo/AddInfo.php?mid=4&enews=AddInfo", "/e/DoInfo/AddInfo.php?mid=7", 
          "/e/DoInfo/AddInfo.php?mid=8", "/e/DoInfo/AddInfo.php", "/e/member/AddInfo.php"]:
    try:
        r = op.open(f"{B}{p}", timeout=10)
        b = r.read().decode("gbk","ignore")
        print(f"=== {p} [{len(b)}B] ===", flush=True)
        if len(b) > 1900:
            # 表单和上传字段
            for m in re.findall(r"<form[^>]*>", b)[:3]:
                print("  FORM:", m[:150], flush=True)
            for m in re.findall(r'<input[^>]*type="(?:file|hidden)"[^>]*name="([^"]*)"[^>]*>', b)[:10]:
                print("  INPUT:", m, flush=True)
            for m in re.findall(r'<iframe[^>]*src="([^"]*)"', b)[:5]:
                print("  IFRAME:", m, flush=True)
            if "upload" in b.lower() or "上传" in b or "editor" in b.lower():
                print("  >>> 含编辑器/上传!", flush=True)
    except Exception as e:
        print(f"=== {p} ERR {str(e)[:50]} ===", flush=True)
