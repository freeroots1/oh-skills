#!/usr/bin/env python3
"""haitai_pboot.py - haitaicasting.com PbootCMS后台探测"""
import urllib.request, urllib.parse, ssl, re

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

def fetch(url, timeout=8, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
            headers={**UA, 'Content-Type': 'application/x-www-form-urlencoded'} if data else UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read(80000).decode('utf-8', 'ignore'), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(80000).decode('utf-8', 'ignore'), e.geturl()
    except Exception as e:
        return 0, repr(e)[:100], ''

BASE = 'http://haitaicasting.com'
print('=== admin.php ===')
st, b, fu = fetch(BASE + '/admin.php')
print('st=%d size=%d fu=%s' % (st, len(b), fu))
inputs = re.findall(r'<input[^>]*name="([^"]+)"', b)
print('fields:', inputs[:10])
print('has captcha:', 'captcha' in b.lower() or '验证码' in b)
forms = re.findall(r'<form[^>]*action="([^"]*)"', b)
print('form:', forms[:2])

print('\n=== PbootCMS版本 ===')
st, b, fu = fetch(BASE + '/')
for m in re.finditer(r'pbootcms[\s\S]{0,40}|Powered by[^<]{0,40}|v[0-9]\.[0-9]\.[0-9]', b, re.I):
    print('  mark:', m.group(0)[:60])
