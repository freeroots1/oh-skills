#!/usr/bin/env python3
"""st_test2.py - 完整登录响应分析"""
import urllib.request, urllib.parse, ssl, re, sys, io
import ddddocr
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}

ocr = ddddocr.DdddOcr(show_ad=False)
ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)

r = urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:13080/st_cap.jpg', headers=UA), timeout=15, context=ctx)
img = r.read()
c1 = ocr.classification(img)
try:
    im = Image.open(io.BytesIO(img)).convert('L')
    im = im.resize((im.width * 4, im.height * 4), Image.LANCZOS)
    im = im.point(lambda p: 255 if p > 120 else 0)
    buf = io.BytesIO(); im.save(buf, 'PNG')
    c2 = ocrb.classification(buf.getvalue())
except Exception:
    c2 = c1
code = c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)

url = 'http://127.0.0.1:13080/login_st.php?u=admin&p=WRONG9&c=' + code
r2 = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25, context=ctx)
resp = r2.read(20000)
idx = resp.find(b'GIF89a')
body = resp[idx+6:] if idx > 0 else resp
print('body len:', len(body))
print('body:', body[:400].decode('utf-8', 'ignore').replace(chr(10), ' '))
