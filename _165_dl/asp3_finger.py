#!/usr/bin/env python3
"""asp3_finger.py - 3个老站首页指纹细化"""
import urllib.request, ssl, re

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

def fetch(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read(100000), r.geturl(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(100000), e.geturl(), dict(e.headers)
    except Exception as e:
        return 0, repr(e).encode(), '', {}

for d in ['haitaicasting.com', 'huxhardware.com', 'oiwas.com']:
    print('===== %s =====' % d, flush=True)
    st, b, fu, hd = fetch('http://' + d + '/')
    print('st=%d size=%d server=%s powered=%s' % (st, len(b), hd.get('Server', '')[:25], hd.get('X-Powered-By', '')[:25]))
    low = b.decode('utf-8', 'ignore').lower()
    # 找页面内的asp/php/aspx引用
    exts = re.findall(r'\.(asp|aspx|php|jsp|html)\??[^"\']*', low)
    from collections import Counter
    print('ext refs:', Counter(exts).most_common(5))
    # 生成器
    gen = re.findall(r'generator[^>]*content="([^"]*)"', low)
    if gen:
        print('generator:', gen[:2])
    # 首页链接(找后台线索)
    links = re.findall(r'href="([^"]*(?:admin|manage|login|user)[^"]*)"', low)
    print('admin links:', links[:5])
    # 标题
    m = re.search(r'<title>([^<]{2,60})</title>', low)
    if m:
        print('title:', m.group(1))
    print('', flush=True)
