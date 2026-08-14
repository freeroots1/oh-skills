#!/usr/bin/env python3
"""tp_rce_verify2.py - 严格验证v2: 排除CF挑战页/URL反射
真RCE特征: mark以纯文本出现(非URL编码/非JS变量), 页面非CF挑战
"""
import urllib.request, urllib.parse, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
MARK = 'tprce_mark_8842'

def fetch_raw(url, timeout=12):
    try:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=ctx))
        req = urllib.request.Request(url, headers=UA)
        r = opener.open(req, timeout=timeout)
        return r.status, r.read(50000).decode('utf-8', 'ignore'), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(50000).decode('utf-8', 'ignore'), e.geturl()
    except Exception:
        return 0, '', ''

def is_real_rce(b, url):
    # 排除CF挑战
    if 'cf_chl' in b or 'z0f76a1d14fd21' in b or 'challenge-platform' in b:
        return False, 'cloudflare-challenge'
    # 排除URL反射: mark出现但被URL编码包裹
    if MARK in b:
        pos = b.find(MARK)
        ctx = b[max(0,pos-80):pos+len(MARK)+20]
        # 真RCE: mark是printf输出, 前面没有URL编码(%26/%3D/%5B)
        if '%26' in ctx or '%3D' in ctx or '%5B' in ctx or '\\u0026' in ctx:
            return False, 'url-encoded-reflect: ' + ctx[:100]
        # 纯文本出现
        return True, 'raw: ' + ctx.replace(chr(10), ' ')[:100]
    return False, 'mark-not-found'

def main():
    real = []
    with open('/tmp/tp_rce_verified.txt') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                dom, name, url = parts[0], parts[1], parts[2]
                st, b, fu = fetch_raw(url)
                ok, reason = is_real_rce(b, url)
                if ok:
                    print('REAL RCE: %s [%s] st=%d %s' % (dom, name, st, reason), flush=True)
                    real.append((dom, name, url))
                else:
                    print('FALSE: %s [%s] st=%d %s' % (dom, name, st, reason[:80]), flush=True)
    print('=== REAL: %d ===' % len(real), flush=True)
    with open('/tmp/tp_rce_real.txt', 'w') as f:
        for r in real:
            f.write('\t'.join(r) + '\n')

if __name__ == '__main__':
    main()
