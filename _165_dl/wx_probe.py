#!/usr/bin/env python3
"""wxiajin 探测上传功能"""
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

targets = [
    "/e/member/EditInfo/",
    "/e/DoInfo/ListInfo.php?mid=4",
    "/e/member/mspace/SetSpace.php",
    "/e/member/EditInfo/AddInfo.php?mid=4",
    "/e/DoInfo/AddInfo.php?mid=4",
]
for p in targets:
    try:
        r = op.open(f"{B}{p}", timeout=10)
        b = r.read().decode("gbk","ignore")
        forms = re.findall(r'<form[^>]*action="([^"]*)"[^>]*>', b)
        inputs = re.findall(r'<input[^>]*type="(file|hidden)"[^>]*name="([^"]*)"[^>]*>', b)
        print(f"=== {p} [{len(b)}B] ===", flush=True)
        print("  actions:", forms[:5], flush=True)
        print("  file/hidden:", inputs[:10], flush=True)
        if "上传" in b or "upload" in b.lower():
            print("  >>> 含上传功能!", flush=True)
            for m in re.findall(r'<input[^>]*type="file"[^>]*>', b)[:5]:
                print("   ", m[:150], flush=True)
    except Exception as e:
        print(f"=== {p} ERR {str(e)[:50]} ===", flush=True)
