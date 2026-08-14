#!/usr/bin/env python3
"""wxiajin 详细表单分析"""
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

for p in ["/e/member/EditInfo/", "/e/member/mspace/SetSpace.php"]:
    b = op.open(f"{B}{p}", timeout=10).read().decode("gbk","ignore")
    print(f"===== {p} =====", flush=True)
    # 表单
    for m in re.findall(r"<form[^>]*>", b):
        print("FORM:", m[:200], flush=True)
    # 所有input
    for m in re.findall(r"<input[^>]*>", b):
        if any(k in m.lower() for k in ["file", "upload", "submit", "text", "hidden"]):
            print("INPUT:", m[:150], flush=True)
    # select
    for m in re.findall(r"<select[^>]*name=\"([^\"]*)\"", b):
        print("SELECT:", m, flush=True)
    # textarea
    for m in re.findall(r"<textarea[^>]*name=\"([^\"]*)\"", b):
        print("TEXTAREA:", m, flush=True)
    print("", flush=True)
