#!/usr/bin/env python3
"""sz_confirm_hit.py - 严格验证admin/sadwj (带cookie+看跳转)"""
import urllib.request, urllib.parse, ssl, re, sys, time, io, http.cookiejar
import ddddocr
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
GETCAP = 'http://127.0.0.1:13080/getcap_sz.php'
CAPIMG = 'http://127.0.0.1:13080/sz_cap.jpg'
LOGIN = 'http://127.0.0.1:13080/login_sz.php'

def fetch(url, timeout=25):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.read(40000)
    except Exception:
        return b''

ocr = ddddocr.DdddOcr(show_ad=False)
ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)

# 验证3次确认稳定性
for round_n in range(3):
    print('=== round %d ===' % round_n, flush=True)
    for attempt in range(10):
        out = fetch(GETCAP + '?d=szsadwj.com')
        if b'SAVED:' not in out:
            continue
        img = fetch(CAPIMG)
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
        out = fetch(LOGIN + '?d=szsadwj.com&u=admin&p=sadwj&c=' + code)
        idx = out.find(b'GIF89a')
        body = out[idx+6:] if idx > 0 else out
        text = body.decode('gb2312', 'ignore') if body else ''
        if '确认码' in text or '不一致' in text:
            continue
        print('  len=%d text=%s' % (len(body), text[:120].replace(chr(10), ' ')), flush=True)
        break
    time.sleep(2)
print('=== done ===', flush=True)
