#!/usr/bin/env python3
"""probe_compare3.py - 单次登录看完整响应"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'https://www.compared4u.net'
LOGIN = BASE + '/dede/login.php'

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
opener.open(urllib.request.Request(LOGIN, headers=UA), timeout=10).read()

data = urllib.parse.urlencode({'dopost': 'login', 'userid': 'admin', 'pwd': 'admin',
                               'gotopage': '/dede/index.php', 'validate': ''}).encode()
req = urllib.request.Request(LOGIN, data=data, headers={**UA, 'Content-Type': 'application/x-www-form-urlencoded', 'Referer': LOGIN})
r = opener.open(req, timeout=10)
b = r.read(30000).decode('utf-8', 'ignore')
print('st:', r.status, 'fu:', r.geturl())
# 提取中文
cns = re.findall(r'[\u4e00-\u9fff]{3,}', b)
print('中文:', cns[:10])
# 是否有登录表单(说明被重定向回登录页)
print('has login form:', 'userPass' in b or 'userName' in b)
print('has captcha msg:', '验证码' in b)
print('has error msg:', '错误' in b or '失败' in b or '不正确' in b)
print('body head:', b[:300].replace(chr(10), ' '))
