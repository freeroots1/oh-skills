#!/usr/bin/env python3
"""haitai_fc.py - 检查haitaicasting登录页formcheck"""
import urllib.request, ssl, re, http.cookiejar

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'http://haitaicasting.com'
LOGIN = BASE + '/admin.php?p=/Index/login'

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
r = opener.open(urllib.request.Request(LOGIN, headers=UA), timeout=10)
b = r.read(50000).decode('utf-8', 'ignore')
print('size:', len(b))
# formcheck
for m in re.finditer(r'formcheck', b):
    s = b[max(0, m.start()-30):m.start()+80].replace(chr(10), ' ')
    print('FC:', s)
# input字段
for m in re.finditer(r'<input[^>]*>', b):
    t = m.group(0)
    if 'check' in t.lower() or 'user' in t.lower() or 'pass' in t.lower():
        print('INPUT:', t[:150])
# script里的formcheck赋值
for m in re.finditer(r'.{0,50}formcheck.{0,100}', b):
    print('JS:', m.group(0).replace(chr(10), ' ')[:180])
