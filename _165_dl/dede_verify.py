#!/usr/bin/env python3
"""dede_verify.py - 验证DedeCMS目标真实性+版本+漏洞探测"""
import urllib.request, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

def fetch(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read(60000).decode('utf-8', 'ignore'), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(60000).decode('utf-8', 'ignore'), e.geturl()
    except Exception:
        return 0, '', ''

targets = ['chinaglass.club', 'cocilux2009.com', 'daiseyiowa.daiseysolutions.org',
           'danburyfencing.com', 'dimaikj.com', 'dollyhouse.net']

for d in targets:
    print('=== %s ===' % d, flush=True)
    # 首页
    st, body, fu = fetch('http://' + d)
    marks = []
    low = body.lower()
    for k in ['dedecms', 'dede', '织梦', 'templets', 'powered by']:
        if k in low:
            marks.append(k)
    # 常见路径
    paths = {}
    for p in ['/dede/', '/dede/login.php', '/data/admin/ver.txt', '/plus/download.php',
              '/member/index.php', '/include/inc/inc_version.php']:
        st2, b2, _ = fetch('http://' + d + p)
        paths[p] = (st2, len(b2))
    print('  home: st=%d size=%d marks=%s' % (st, len(body), marks[:3]), flush=True)
    for p, (s, l) in paths.items():
        print('  %s -> %d/%d' % (p, s, l), flush=True)
    # ver.txt 版本
    st3, b3, _ = fetch('http://' + d + '/data/admin/ver.txt')
    if st3 == 200 and len(b3) < 200:
        print('  VERSION: %s' % b3.strip()[:60], flush=True)
    print('', flush=True)
