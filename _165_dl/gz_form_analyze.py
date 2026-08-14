#!/usr/bin/env python3
"""gz: analyze adddrugs form - factory options, required fields; submit complete"""
import urllib.request, urllib.parse, re, http.cookiejar, base64, subprocess, sys, uuid

HOST = "http://gz-dichuan.com"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def ocr(img_bytes):
    b64 = base64.b64encode(img_bytes).decode()
    code = "import ddddocr,base64; o=ddddocr.DdddOcr(show_ad=False); print(o.classification(base64.b64decode('%s')))" % b64
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=20, cwd="/tmp")
    return r.stdout.decode().strip()

cj = http.cookiejar.CookieJar()
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

for attempt in range(10):
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
            print("login ok")
            break
    except Exception:
        pass

# get adddrugs page and analyze factory options + required
code, final, body = fetch(HOST + "/index.php?m=admin&c=goods&a=adddrugs",
                          headers={"Referer": HOST + "/index.php?m=admin&c=index&a=index"})
bt = body.decode("utf-8", "ignore")
# factory select options
opts = re.findall(r'<option[^>]*value=["\'](\d+)["\'][^>]*>([^<]*)</option>', bt)
print("factory options:", opts[:10])
# required markers
reqs = re.findall(r'<[^>]*required[^>]*>', bt)
print("required fields:", reqs[:5])
# textarea/editor fields
editors = re.findall(r'UE\.getEditor\(([^)]+)\)', bt)
print("UEditor fields:", editors)
# hidden fields
hiddens = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*name=["\']([^"\']+)["\'][^>]*value=["\']([^"\']*)["\']', bt)
print("hiddens:", hiddens[:10])
# select fields
for sel in re.findall(r'<select[^>]*name=["\']([^"\']+)["\']', bt):
    print("select field:", sel)
