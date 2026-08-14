#!/usr/bin/env python3
"""verify_jvl.py - jewishvirtuallibrary.org /admin/ 深挖"""
import urllib.request, urllib.parse, ssl, re

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read(50000).decode('utf-8', 'ignore'), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(50000).decode('utf-8', 'ignore'), e.geturl()
    except Exception as e:
        return 0, repr(e)[:100], ''

st, b, fu = fetch('https://jewishvirtuallibrary.org/admin/')
print('st=%d size=%d fu=%s' % (st, len(b), fu))
print('title:', re.search(r'<title>([^<]*)</title>', b, re.I).group(1) if re.search(r'<title>([^<]*)</title>', b, re.I) else '?')
inputs = re.findall(r'<input[^>]*name="([^"]+)"', b)
print('fields:', inputs[:10])
print('has login:', 'login' in b.lower() or 'password' in b.lower() or '登录' in b)
# 后台特征
for k in ['dedecms', 'wordpress', 'drupal', 'joomla', 'admin']:
    if k in b.lower():
        print('  cms mark:', k)
