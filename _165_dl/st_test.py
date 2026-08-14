#!/usr/bin/env python3
"""st_test.py - 测试sunten验证码OCR+登录"""
import urllib.request, urllib.parse, ssl, re, sys, io
import ddddocr
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}

ocr = ddddocr.DdddOcr(show_ad=False)
ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)

# 拉验证码
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
print('OCR1: %s OCR2: %s' % (c1, c2), flush=True)
code = c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)
print('using:', code, flush=True)

# 登录测试(错误密码看响应)
url = 'http://127.0.0.1:13080/login_st.php?u=admin&p=WRONG9&c=' + code
r2 = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25, context=ctx)
resp = r2.read(10000).decode('utf-8', 'ignore')
print('login resp:', resp[:200].replace(chr(10), ' '), flush=True)
