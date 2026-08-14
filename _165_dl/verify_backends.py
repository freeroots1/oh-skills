#!/usr/bin/env python3
"""verify_backends.py - 验证637清单里的后台真实性+技术栈
检查: 响应是否源码泄露/CF/真实登录表单/可执行
"""
import urllib.request, ssl, socket, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

socket.setdefaulttimeout(5)
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

def fetch(url, timeout=6):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.status, r.read(30000).decode('utf-8', 'ignore'), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(30000).decode('utf-8', 'ignore'), e.geturl()
    except Exception:
        return 0, '', ''

def verify(dom, path):
    url = 'http://' + dom + path
    st, b, fu = fetch(url)
    if st != 200 or len(b) < 500:
        return None
    low = b.lower()
    if 'cdn-cgi' in low or 'challenge-platform' in low or 'z0f76' in low:
        return (dom, path, 'CF-BLOCKED', len(b))
    if b.startswith('<?php') or b.startswith('<?xml'):
        return (dom, path, 'SOURCE-LEAK', len(b))
    # 登录表单
    has_pw = 'type="password"' in low or 'password' in low or 'pwd' in low
    has_user = 'username' in low or 'userid' in low or 'user_name' in low or 'loginname' in low
    fields = re.findall(r'<input[^>]*name="([^"]+)"', low)
    if has_pw and has_user:
        return (dom, path, 'LOGIN', len(b), fields[:6])
    # 其他: 可能是管理页或占位
    return (dom, path, 'PAGE(%d)' % len(b), len(b))

def main():
    entries = []
    with open('/tmp/cms_backends.tsv') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                entries.append((parts[0], parts[1]))
    print('entries: %d' % len(entries), flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(verify, d, p): (d, p) for d, p in entries}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception:
                r = None
            if r:
                results.append(r)
                if r[2] in ('LOGIN', 'SOURCE-LEAK'):
                    print('V: %s\t%s\t%s\t%s' % (r[0], r[1], r[2], r[3]), flush=True)
    with open('/tmp/backends_verified.tsv', 'w') as f:
        for r in results:
            f.write('\t'.join(str(x) for x in r) + '\n')
    print('[done] %d results' % len(results), flush=True)

if __name__ == '__main__':
    main()
