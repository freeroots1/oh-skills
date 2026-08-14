#!/usr/bin/env python3
"""convertmypdftoword.com - PDF converter: upload php disguised + check response
Also hemeixinpcb.com upload form deep probe
"""
import urllib.request, urllib.parse, re, http.cookiejar, uuid, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0"}

def get_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)), cj

def fetch(op, url, timeout=12, data=None, files=None, referer=None):
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
        return r.status, r.geturl(), r.read(80000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)[:80]

# --- convertmypdftoword.com ---
print("=== convertmypdftoword.com ===", flush=True)
op, cj = get_opener()
code, final, body = fetch(op, "https://convertmypdftoword.com/")
print("home: %s final=%s size=%d" % (code, final[:40], len(body)), flush=True)
# find upload form
forms = re.findall(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>', body, re.I)
print("forms:", forms[:4], flush=True)
files = re.findall(r'<input[^>]*type=["\']file["\'][^>]*name=["\']([^"\']*)["\']', body, re.I)
print("file inputs:", files[:3], flush=True)
# find upload JS/endpoints
for kw in ["upload", "convert", "api", "dropzone", "plupload"]:
    for m in list(re.finditer(kw, body, re.I))[:3]:
        i = m.start()
        print("KW[%s]: ...%s..." % (kw, body[max(0,i-50):i+60].replace("\n", " ")[:100]), flush=True)

# --- hemeixinpcb.com ---
print("\n=== hemeixinpcb.com ===", flush=True)
op2, cj2 = get_opener()
code, final, body2 = fetch(op2, "https://www.hemeixinpcb.com/")
print("home: %s size=%d" % (code, len(body2)), flush=True)
forms2 = re.findall(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>', body2, re.I)
print("forms:", forms2[:4], flush=True)
files2 = re.findall(r'<input[^>]*type=["\']file["\'][^>]*name=["\']([^"\']*)["\']', body2, re.I)
print("file inputs:", files2[:3], flush=True)
