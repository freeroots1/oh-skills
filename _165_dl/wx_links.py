#!/usr/bin/env python3
"""wxiajin 会员中心链接提取"""
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
b = op.open(f"{B}/e/member/cp/", timeout=10).read().decode("gbk","ignore")

print("=== 会员中心文本内容 ===")
txt = re.sub(r"<[^>]+>", " ", b)
txt = re.sub(r"\s+", " ", txt)
print(txt[:600])
print("")
print("=== 所有链接 ===")
for m in re.finditer(r'href="([^"]+)"[^>]*>', b):
    u = m.group(1)
    print(u)
