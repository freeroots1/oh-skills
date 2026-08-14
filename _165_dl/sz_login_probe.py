#!/usr/bin/env python3
"""sz_login_probe.py - szsadwj登录响应分析"""
import urllib.request, urllib.parse, ssl, re

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}

def fetch(url, timeout=25):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.read(40000)
    except Exception as e:
        return repr(e).encode()

# 测试登录(错误密码)
out = fetch('http://127.0.0.1:13080/login_sz.php?d=szsadwj.com&u=admin&p=WRONG9&c=1234')
# 从GIF89a后开始解析
idx = out.find(b'GIF89a')
body = out[idx+6:] if idx > 0 else out
# 提取中文(GB2312)
try:
    text = body.decode('gb2312', 'ignore')
    # 提取可见文本
    texts = re.findall(r'[\u4e00-\u9fff]{2,}', text)
    print('中文:', texts[:8])
except Exception as e:
    print('decode err', e)
# 也看原始HTML title/script
print('has script:', b'<script' in body.lower())
print('len:', len(body))
