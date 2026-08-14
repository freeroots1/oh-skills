#!/usr/bin/env python3
"""st_diag.py - 诊断sunten爆破问题"""
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
    except Exception as e:
        return ('ERR:' + repr(e)[:50]).encode()

# 1. 验证码下载10次看成功率
ok = 0
for i in range(10):
    out = fetch(HOST + '/getcap_st.php')
    if b'SAVED:' in out:
        ok += 1
    time.sleep(1)
print('getcap success: %d/10' % ok, flush=True)

# 2. 拉图+OCR 5次
for i in range(5):
    img = fetch(HOST + '/st_cap.jpg')
    if len(img) < 50:
        print('cap img fail len=%d' % len(img), flush=True)
        continue
    try:
        c1 = ocr.classification(img)
        im = Image.open(io.BytesIO(img)).convert('L')
        im = im.resize((im.width * 4, im.height * 4), Image.LANCZOS)
        im = im.point(lambda p: 255 if p > 120 else 0)
        buf = io.BytesIO(); im.save(buf, 'PNG')
        c2 = ocrb.classification(buf.getvalue())
    except Exception as e:
        print('ocr err:', repr(e)[:60], flush=True)
        continue
    print('cap%d: %s / %s' % (i, c1, c2), flush=True)
    time.sleep(1)

# 3. 登录1次看原始响应
img = fetch(HOST + '/st_cap.jpg')
c1 = ocr.classification(img)
code = c1
out = fetch(HOST + '/login_st.php?u=admin&p=WRONG&c=' + code)
idx = out.find(b'GIF89a')
body = out[idx+6:] if idx > 0 else out
print('login raw:', body[:200], flush=True)
