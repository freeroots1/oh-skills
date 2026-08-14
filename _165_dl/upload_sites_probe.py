#!/usr/bin/env python3
"""upload_sites_probe.py - 批量验证UPLOAD站点技术栈+上传接口"""
import urllib.request, urllib.parse, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

SITES = ['ahbill.com', 'ahhzlq.com', 'ahlhby.com', 'ahsjkx.net', 'ahxiyy.com',
         'ahhubang.com', 'ahygfz.com', 'ahyxfh.com', 'ahyyhb.net', 'ahzfgg.com']

def fetch(url, timeout=12):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.status, r.read(60000).decode('utf-8', 'ignore')
    except urllib.error.HTTPError as e:
        return e.code, e.read(60000).decode('utf-8', 'ignore')
    except Exception as e:
        return 0, repr(e)[:60]

for dom in SITES:
    st, b = fetch('http://' + dom + '/')
    low = b.lower()
    # 技术栈
    stack = []
    if '.aspx' in low or 'asp.net' in low or '__viewstate' in low:
        stack.append('aspnet')
    if 'dedecms' in low or '织梦' in b:
        stack.append('dedecms')
    if 'pboot' in low or 'pb_' in low:
        stack.append('pbootcms')
    if 'thinkphp' in low or 'tp_' in low:
        stack.append('thinkphp')
    if 'wordpress' in low or 'wp-content' in low:
        stack.append('wordpress')
    if '.php' in low:
        stack.append('php')
    if 'empirecms' in low or '帝国' in b:
        stack.append('empire')
    # 上传表单
    up_form = re.findall(r'<form[^>]*enctype="multipart/form-data"[^>]*action="([^"]*)"', b, re.I)
    file_in = re.findall(r'<input[^>]*type="file"[^>]*name="([^"]+)"', b, re.I)
    print('%s: st=%d size=%d stack=%s upload_action=%s file_fields=%s' %
          (dom, st, len(b), '/'.join(stack) if stack else '?', up_form[:2], file_in[:3]), flush=True)
