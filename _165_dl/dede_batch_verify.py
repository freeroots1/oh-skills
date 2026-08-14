#!/usr/bin/env python3
"""dede_batch_verify.py - 批量验证DedeCMS候选
检查 /dede/login.php 是否存在 + 首页指纹 + 版本
输出: /tmp/dede_real.tsv
"""
import urllib.request, urllib.parse, ssl, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0'}

def fetch(url, timeout=7):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read(60000).decode('utf-8', 'ignore'), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(60000).decode('utf-8', 'ignore'), e.geturl()
    except Exception:
        return 0, '', ''

def verify(dom):
    result = None
    # 1. /dede/login.php
    st, b, fu = fetch('http://' + dom + '/dede/login.php')
    if st == 200 and len(b) > 500:
        has_login = 'password' in b.lower() or 'pwd' in b.lower() or 'userid' in b.lower()
        has_captcha = 'vdimgck' in b.lower() or 'captcha' in b.lower() or '验证码' in b
        if has_login:
            result = ('dede-login', dom, '/dede/login.php', len(b), has_captcha)
            return result
    # 2. 首页指纹
    st, b, fu = fetch('http://' + dom + '/')
    if st == 200 and len(b) > 2000:
        marks = []
        for k in ['dedecms', 'dede', '织梦', 'templets']:
            if k in b.lower():
                marks.append(k)
        if marks:
            # 版本
            ver = ''
            m = re.search(r'dede:(\d+)', b)
            if m:
                ver = m.group(1)
            result = ('dede-home', dom, '/', len(b), ver or ','.join(marks[:2]))
            return result
    return None

def main():
    doms = open('/tmp/dede_clean.txt').read().strip().split('\n')
    print('targets: %d' % len(doms), flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(verify, d): d for d in doms}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception:
                r = None
            if r:
                results.append(r)
                print('\t'.join(str(x) for x in r), flush=True)
    with open('/tmp/dede_real.tsv', 'w') as f:
        for r in results:
            f.write('\t'.join(str(x) for x in r) + '\n')
    print('=== DONE: %d real ===' % len(results), flush=True)

if __name__ == '__main__':
    main()
