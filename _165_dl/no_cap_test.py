#!/usr/bin/env python3
"""no_cap_test.py - 测试无验证码站直接登录"""
import urllib.request, urllib.parse, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
SHELL = 'http://127.0.0.1:13080/loginpost2.php'

# 登录post2的字段固定username/password/Code - 对无验证码站可能不适用
# 改用theme_check? 已被杀. 用proxy_t GET方式测试表单结构
PROXY = 'http://127.0.0.1:13080/proxy_t.php'

def fetch_proxy(url):
    purl = PROXY + '?u=' + urllib.parse.quote(url, safe='')
    try:
        r = urllib.request.urlopen(urllib.request.Request(purl, headers=UA), timeout=15, context=ctx)
        b = r.read(30000)
        if b[:1] == b'[':
            m = re.match(rb'\[(\d+)\]', b)
            return int(m.group(1)), b[m.end():].decode('gbk', 'ignore')
        return r.status, b.decode('gbk', 'ignore')
    except Exception as e:
        return 0, str(e)

# 检查5084模板站的表单字段
for dom in ['www.ntyq.cn', 'xwrubber.cn', 'xidipipe.com']:
    st, body = fetch_proxy('http://' + dom + '/admin/login.asp')
    fields = re.findall(r'<input[^>]*name="([^"]+)"', body)
    action = re.findall(r'<form[^>]*action="([^"]*)"', body)
    imgs = re.findall(r'<img[^>]*src="([^"]*)"', body)
    print('%s: fields=%s action=%s imgs=%s' % (dom, fields[:6], action[:2], imgs[:4]), flush=True)
