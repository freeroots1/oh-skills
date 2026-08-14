#!/usr/bin/env python3
"""st_quick_test.py - 验证码快测: getcap后立即OCR立即提交"""
import urllib.request, urllib.parse, ssl, re, sys, time, io, json
import ddddocr
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
HOST = 'http://127.0.0.1:13080'

ocr = ddddocr.DdddOcr(show_ad=False)
ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)

def fetch(url, timeout=30):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.read(30000)
    except Exception:
        return b''

# 快速循环: getcap->OCR->login 无间隔
for i in range(8):
    out = fetch(HOST + '/getcap_st.php')
    if b'SAVED:' not in out:
        print('round%d: getcap fail' % i, flush=True)
        continue
    img = fetch(HOST + '/st_cap.jpg')
    if not img or len(img) < 50:
        print('round%d: img fail' % i, flush=True)
        continue
    try:
        c1 = ocr.classification(img)
        im = Image.open(io.BytesIO(img)).convert('L')
        im = im.resize((im.width * 4, im.height * 4), Image.LANCZOS)
        im = im.point(lambda p: 255 if p > 120 else 0)
        buf = io.BytesIO(); im.save(buf, 'PNG')
        c2 = ocrb.classification(buf.getvalue())
    except Exception:
        print('round%d: ocr fail' % i, flush=True)
        continue
    code = c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)
    out = fetch(HOST + '/login_st.php?u=admin&p=WRONG&c=' + code)
    idx = out.find(b'GIF89a')
    body = out[idx+6:] if idx > 0 else out
    m = re.search(rb'\{[^}]*\}', body)
    if not m:
        print('round%d: nojson code=%s' % (i, code), flush=True)
        continue
    try:
        d = json.loads(m.group(0).decode('utf-8'))
        err = d.get('error')
        if err == 2:
            print('round%d: CAPTCHA WRONG code=%s' % (i, code), flush=True)
        else:
            print('round%d: err=%s msg=%s code=%s <<<<' % (i, err, d.get('msg'), code), flush=True)
    except Exception:
        print('round%d: parse err code=%s' % (i, code), flush=True)
