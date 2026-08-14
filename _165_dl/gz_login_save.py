#!/usr/bin/env python3
"""gz: login (robust), dump adddrugs form for analysis, save cookies"""
import urllib.request, urllib.parse, re, http.cookiejar, base64, subprocess, sys, os

HOST = "http://gz-dichuan.com"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
CJFILE = "/tmp/gz_cj.txt"

cj = http.cookiejar.MozillaCookieJar(CJFILE)
if os.path.exists(CJFILE):
    try:
        cj.load(ignore_discard=True, ignore_expires=True)
    except Exception:
        pass
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch(url, data=None, timeout=15, headers=None, raw=None):
    h = {**UA}
    if raw:
        h["Content-Type"] = "multipart/form-data; boundary=" + raw[0]
    else:
        h["Content-Type"] = "application/x-www-form-urlencoded"
    if headers: h.update(headers)
    try:
        body = raw[1] if raw else (data.encode() if data else None)
        req = urllib.request.Request(url, data=body, headers=h)
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, url, e.read()
    except Exception as ex:
        return 0, url, str(ex).encode()

def ocr(img_bytes):
    b64 = base64.b64encode(img_bytes).decode()
    code = "import ddddocr,base64; o=ddddocr.DdddOcr(show_ad=False); print(o.classification(base64.b64decode('%s')))" % b64
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=20, cwd="/tmp")
    return r.stdout.decode().strip()

# check if already logged in
code, final, body = fetch(HOST + "/index.php?m=admin&c=goods&a=adddrugs",
                          headers={"Referer": HOST + "/index.php?m=admin&c=index&a=index"})
if b"drugs_name" in body:
    print("already logged in")
else:
    for attempt in range(15):
        try:
            code, final, body = fetch(HOST + "/index.php?m=admin&c=login&a=index")
            code, final, cap = fetch(HOST + "/index.php?m=admin&c=login&a=vertify",
                                     headers={"Referer": HOST + "/index.php?m=admin&c=login&a=index"})
            cap_text = ocr(cap)
            data = urllib.parse.urlencode({"username": "admin", "password": "admin123", "vertify": cap_text})
            code, final, resp = fetch(HOST + "/index.php?m=admin&c=login&a=login", data=data,
                                      headers={"Referer": HOST + "/index.php?m=admin&c=login&a=index",
                                               "X-Requested-With": "XMLHttpRequest"})
            rt = resp.decode("utf-8", "ignore")
            if "登录成功" in rt or '"status":1' in rt:
                print("login ok (attempt %d OCR=%s)" % (attempt, cap_text))
                cj.save(ignore_discard=True, ignore_expires=True)
                break
        except Exception:
            pass
    else:
        print("login FAILED after 15 attempts")
        sys.exit(1)
    code, final, body = fetch(HOST + "/index.php?m=admin&c=goods&a=adddrugs",
                              headers={"Referer": HOST + "/index.php?m=admin&c=index&a=index"})

bt = body.decode("utf-8", "ignore")
open("/tmp/gz_adddrugs_full.html", "w").write(bt)
print("adddrugs size:", len(bt))
# analyze form
opts = re.findall(r'<option[^>]*value=["\'](\d+)["\'][^>]*>([^<]*)</option>', bt)
print("factory options:", opts[:15])
for sel in re.findall(r'<select[^>]*name=["\']([^"\']+)["\']', bt):
    print("select:", sel)
reqs = re.findall(r'<input[^>]*name=["\']([^"\']+)["\'][^>]*(required|style="[^"]*color[^"]*red)', bt, re.I)
print("maybe-required:", reqs[:10])
editors = re.findall(r'UE\.getEditor\(["\']([^"\']+)["\']', bt)
print("UEditor fields:", editors)
hiddens = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*name=["\']([^"\']+)["\'][^>]*>', bt)
print("hidden fields:", hiddens)
