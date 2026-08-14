#!/usr/bin/env python3
"""zhongsheng ThinkPHP admin login with captcha OCR"""
import urllib.request, urllib.parse, re, http.cookiejar, base64, subprocess, sys

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://zhongshengjinshuzhipin.com"
LOGIN_URL = "/index.php?g=admin&m=public&a=login"

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

# find captcha URL from login page
op, cj = get_opener()
code, final, body = fetch(op, HOST + LOGIN_URL)
print("login: %s size=%d" % (code, len(body)), flush=True)
# captcha image src
cap_src = re.findall(r'(?:src|data-url|url)["\']?\s*[:=]\s*["\']([^"\']*(?:captcha|verify|code)[^"\']*)["\']', body, re.I)
print("captcha src:", cap_src[:3], flush=True)
# also look in js
for m in re.finditer(r'["\']([^"\']*(?:verify|captcha|code)[^"\']*(?:\.png|\.gif|\.jpg|\.php|verify)[^"\']*)["\']', body, re.I):
    u = m.group(1)
    if 'http' not in u:
        print("cap candidate:", u, flush=True)

# common ThinkPHP captcha endpoints
for p in ["/index.php?g=admin&m=public&a=verify", "/index.php/Admin/Public/verify",
          "/index.php?m=Admin&c=Public&a=verify"]:
    code, final, body2 = fetch(op, HOST + p)
    if code == 200 and len(body2) > 100 and "PNG" in body2[:20].upper() or "GIF" in body2[:20].upper():
        print("CAPTCHA endpoint: %s (%d bytes)" % (p, len(body2)), flush=True)
        open("/tmp/zs_cap.png", "wb").write(body2.encode("latin1"))
        break
