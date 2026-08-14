#!/usr/bin/env python3
"""oiwas_ezeip.py - oiwas.com ezEIP系统探测"""
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
        return 0, repr(e)[:80], ''

BASE = 'http://oiwas.com'
print('=== ezEIP后台路径 ===')
for p in ['/admin/', '/admin/login.asp', '/admin/index.asp', '/manage/', '/ezeip/',
          '/admin/admin.asp', '/admin/login.aspx', '/Login.asp', '/admin/Login.asp']:
    st, b, fu = fetch(BASE + p)
    if st == 200 and len(b) > 300:
        low = b.lower()
        has_login = 'password' in low or 'login' in low or '登录' in b or 'user' in low
        print('%s -> st=%d size=%d %s' % (p, st, len(b), 'LOGIN?' if has_login else ''), flush=True)
    elif st != 404:
        print('%s -> st=%d size=%d' % (p, st, len(b)), flush=True)

print('\n=== 首页后台链接 ===')
st, b, fu = fetch(BASE + '/')
links = re.findall(r'href="([^"]*(?:admin|manage|login|gl|eip)[^"]*)"', b, re.I)
print('links:', links[:10])
