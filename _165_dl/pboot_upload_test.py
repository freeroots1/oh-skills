#!/usr/bin/env python3
"""pboot_upload_test.py - ahbill.com PbootCMS diyform上传测试"""
import urllib.request, urllib.parse, ssl, re, sys, io

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

def fetch(url, timeout=15):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.status, r.read(50000).decode('utf-8', 'ignore')
    except urllib.error.HTTPError as e:
        return e.code, e.read(50000).decode('utf-8', 'ignore')
    except Exception as e:
        return 0, repr(e)[:80]

# 1. 完整表单分析
st, b = fetch('http://ahbill.com/')
forms = re.findall(r'<form[^>]*>', b)
print('forms:', forms[:3])
# 找diyform字段
fields = re.findall(r'name="([^"]+)"', b)
print('fields:', fields[:15])
# 找上传相关字段
up = re.findall(r'<input[^>]*type="file"[^>]*>', b)
print('file inputs:', up[:3])
# 找隐藏的diyform字段名
hiddens = re.findall(r'<input[^>]*type="hidden"[^>]*>', b)
print('hiddens:', hiddens[:8])
