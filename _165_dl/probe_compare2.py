#!/usr/bin/env python3
"""probe_compare2.py - 找compared4u登录JS接口"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'https://www.compared4u.net'
LOGIN = BASE + '/dede/login.php'

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
r = opener.open(urllib.request.Request(LOGIN, headers=UA), timeout=10)
b = r.read(40000).decode('utf-8', 'ignore')

# 找btnLogin的click处理
for m in re.finditer(r'.{0,200}btnLogin.{0,300}', b):
    s = m.group(0)
    if 'click' in s or 'function' in s or 'ajax' in s.lower() or 'post' in s.lower() or 'url' in s.lower():
        print('JS:', s[:350].replace(chr(10), ' '), flush=True)
        print('---', flush=True)

# 所有script块
for m in re.finditer(r'<script[^>]*>(.*?)</script>', b, re.S):
    s = m.group(1).strip()
    if 'login' in s.lower() or 'userPass' in s or 'ajax' in s.lower():
        print('SCRIPT:', s[:500].replace(chr(10), ' '), flush=True)
        print('---', flush=True)

# 所有 .js 引用
for m in re.finditer(r'src="([^"]*\.js[^"]*)"', b):
    print('JS FILE:', m.group(1), flush=True)
