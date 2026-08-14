#!/usr/bin/env python3
"""find_captcha_backends.py - 并发找usable池里带验证码的后台(攻击器跳过的)"""
import urllib.request, ssl, re, socket
from concurrent.futures import ThreadPoolExecutor, as_completed

socket.setdefaulttimeout(5)
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}

CAP_KEYS = ['captcha', '验证码', 'checkcode', 'imgcode', 'seccode', 'yzm', 'vdimgck', 'verifycode']

def check(dom):
    for path in ['/admin/', '/admin/login.php', '/admin.php', '/login.php', '/manage/']:
        try:
            r = urllib.request.urlopen(urllib.request.Request('http://'+dom+path, headers=UA), timeout=5, context=ctx)
            b = r.read(20000).decode('utf-8','ignore').lower()
            if len(b) > 300 and any(k in b for k in CAP_KEYS):
                return (dom, path)
        except Exception:
            pass
    return None

def main():
    doms = open('/opt/msray/usable_pool.txt').read().split()
    print('total usable: %d' % len(doms), flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=20) as ex:
        futs = {ex.submit(check, d): d for d in doms}
        for fu in as_completed(futs):
            r = fu.result()
            if r:
                results.append(r)
                print('CAPTCHA: %s %s' % r, flush=True)
    with open('/tmp/captcha_backends.txt', 'w') as f:
        for d, p in results:
            f.write('%s\t%s\n' % (d, p))
    print('=== %d captcha backends ===' % len(results), flush=True)

if __name__ == '__main__':
    main()
