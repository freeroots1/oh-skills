#!/usr/bin/env python3
"""verify_north.py - 验证northridgetrading.com DedeCMS后台"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read(40000).decode('utf-8', 'ignore'), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(40000).decode('utf-8', 'ignore'), e.geturl()
    except Exception as e:
        return 0, repr(e)[:100], ''

for scheme in ['http', 'https']:
    st, b, fu = fetch('%s://www.northridgetrading.com/dede/login.php' % scheme)
    print('%s: st=%d size=%d fu=%s' % (scheme, st, len(b), fu[:60]))
    if st == 200 and len(b) > 500:
        inputs = re.findall(r'<input[^>]*name="([^"]+)"', b)
        print('  fields:', inputs[:10])
        print('  has vdimgck:', 'vdimgck' in b.lower())
        print('  has dede:', 'dedecms' in b.lower() or '织梦' in b)
        cns = re.findall(r'[\u4e00-\u9fff]{3,}', b)
        print('  中文:', cns[:5])
        # 验证码URL
        m = re.search(r'src="([^"]*vdimgck[^"]*)"', b)
        if m:
            print('  captcha url:', m.group(1))
        break
