#!/usr/bin/env python3
"""probe_compare.py - 分析compared4u登录提交逻辑"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'https://www.compared4u.net'
LOGIN = BASE + '/dede/login.php'

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
r = opener.open(urllib.request.Request(LOGIN, headers=UA), timeout=10)
b = r.read(30000).decode('utf-8', 'ignore')
print('login page size:', len(b))
# 表单结构
forms = re.findall(r'<form[^>]*action="([^"]*)"[^>]*>', b)
print('form actions:', forms[:3])
inputs = re.findall(r'<input[^>]*>', b)
for i in inputs[:12]:
    print('  INPUT:', i[:120])
# JS提交逻辑
js = re.findall(r'(?:url|action|href)\s*[:=]\s*["\'][^"\']*(?:login|Login|Login|do)[^"\']*["\']', b)
print('js refs:', js[:5])
# 隐藏字段
hiddens = re.findall(r'<input[^>]*type="hidden"[^>]*>', b)
print('hidden:', hiddens[:5])
