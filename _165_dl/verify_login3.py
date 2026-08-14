#!/usr/bin/env python3
"""verify_login3.py - 验证3个无验证码DedeCMS后台"""
import urllib.request, ssl, re

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

for d in ['compared4u.net', 'serviskontrol.com', 'wordstoreality.com']:
    print('=== %s ===' % d, flush=True)
    for scheme in ['http', 'https']:
        st, b, fu = fetch('%s://%s/dede/login.php' % (scheme, d))
        print('  %s: st=%d size=%d fu=%s' % (scheme, st, len(b), fu[:60]), flush=True)
        if st == 200 and len(b) > 500:
            inputs = re.findall(r'<input[^>]*name="([^"]+)"', b)
            has_cap = 'vdimgck' in b.lower() or 'captcha' in b.lower() or '验证码' in b
            has_pw = 'password' in b.lower() or 'type="password"' in b.lower() or 'pwd' in b.lower()
            print('    fields=%s captcha=%s password=%s' % (inputs[:8], has_cap, has_pw), flush=True)
            break
