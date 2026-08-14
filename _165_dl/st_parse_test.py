#!/usr/bin/env python3
"""st_parse_test.py - 测试sunten_bf.py的解析逻辑"""
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

# 模拟sunten_bf逻辑
for i in range(5):
    out = fetch(HOST + '/getcap_st.php')
    if b'SAVED:' not in out:
        print('getcap fail', flush=True)
        continue
    img = fetch(HOST + '/st_cap.jpg')
    if not img or len(img) < 50:
        print('img fail', flush=True)
        continue
    try:
        c1 = ocr.classification(img)
        im = Image.open(io.BytesIO(img)).convert('L')
        im = im.resize((im.width * 4, im.height * 4), Image.LANCZOS)
        im = im.point(lambda p: 255 if p > 120 else 0)
        buf = io.BytesIO(); im.save(buf, 'PNG')
        c2 = ocrb.classification(buf.getvalue())
    except Exception:
        print('ocr fail', flush=True)
        continue
    code = c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)
    out = fetch(HOST + '/login_st.php?u=admin&p=WRONG&c=' + code)
    idx = out.find(b'GIF89a')
    body = out[idx+6:] if idx > 0 else out
    m = re.search(rb'\{[^}]*\}', body)
    if not m:
        print('round%d: nojson! body=%s' % (i, body[:120]), flush=True)
        continue
    try:
        d = json.loads(m.group(0).decode('utf-8'))
        print('round%d: err=%s msg=%s' % (i, d.get('error'), d.get('msg')), flush=True)
    except Exception as e:
        print('round%d: parse err %s raw=%s' % (i, repr(e)[:40], m.group(0)[:80]), flush=True)
    time.sleep(2)
