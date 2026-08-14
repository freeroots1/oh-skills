#!/usr/bin/env python3
"""verify_home3.py - 验证dede-home类型目标"""
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

for d in ['www.jewishvirtuallibrary.org', 'ramglb.com', 'wisevisa.com']:
    print('=== %s ===' % d, flush=True)
    st, b, fu = fetch('http://' + d + '/')
    print('home: st=%d size=%d fu=%s' % (st, len(b), fu[:50]))
    if st == 200:
        low = b.lower()
        print('  dede marks:', [k for k in ['dedecms', '织梦', 'templets', 'dede'] if k in low][:3])
        # 找dede标记上下文
        for k in ['dedecms', '织梦']:
            i = low.find(k)
            if i > 0:
                print('  ctx: %s' % b[max(0, i-50):i+80].replace(chr(10), ' ')[:130])
    # 后台路径
    for p in ['/dede/', '/admin/', '/manage/']:
        st2, b2, fu2 = fetch('http://' + d + p)
        print('  %s: st=%d size=%d' % (p, st2, len(b2)))
