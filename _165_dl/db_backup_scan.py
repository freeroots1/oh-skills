#!/usr/bin/env python3
"""db_backup_scan.py - 专项扫描数据库备份文件泄露(高价值)
找: db.sql / database.sql / dump.sql / backup.sql / *.sql.gz / data.sql / db.sql.gz
判定: 响应以 -- MySQL dump 或 -- MariaDB dump 或 -- phpMyAdmin SQL Dump 开头
"""
import urllib.request, ssl, socket, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

socket.setdefaulttimeout(6)
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}

DB_PATHS = ['/db.sql', '/database.sql', '/dump.sql', '/backup.sql', '/data.sql',
            '/db.sql.gz', '/database.sql.gz', '/backup.sql.gz', '/dump.sql.gz',
            '/mysql.sql', '/sql.sql', '/site.sql', '/www.sql',
            '/db_backup.sql', '/db-backup.sql', '/backup/db.sql', '/backup/database.sql',
            '/1.sql', '/test.sql', '/wp-content/backup.sql', '/sql/dump.sql',
            '/db/database.sql', '/data/database.sql', '/databases.sql']

HITS = '/tmp/db_backup_hits.txt'

def fetch(url, timeout=8):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.status, r.read(2000)  # 只读开头判断
    except urllib.error.HTTPError as e:
        return e.code, e.read(2000)
    except Exception:
        return 0, b''

def check(dom):
    for p in DB_PATHS:
        st, b = fetch('http://'+dom+p)
        if st != 200 or len(b) < 30:
            continue
        head = b.decode('utf-8','ignore','ignore').lower()
        # 真实数据库dump特征
        if ('mysql dump' in head or 'mariadb dump' in head or
            'phpmyadmin sql dump' in head or 'sql dump' in head or
            'create table' in head[:200] or 'insert into' in head[:200]):
            # 排除误报: 不能是HTML
            if '<html' not in head and '<!doctype' not in head:
                return (dom, p, head[:80].replace('\n',' '))

def main():
    doms = set()
    for f in ['/opt/msray/usable_pool.txt', '/opt/msray/alive_pool.txt']:
        try: doms |= set(open(f).read().split())
        except: pass
    doms = list(doms)
    print('targets: %d' % len(doms), flush=True)
    hits = []
    with ThreadPoolExecutor(max_workers=15) as ex:
        futs = {ex.submit(check, d): d for d in doms}
        for i, fu in enumerate(as_completed(futs)):
            r = fu.result()
            if r:
                hits.append(r)
                print('DB-BACKUP: %s %s | %s' % r, flush=True)
            if (i+1) % 500 == 0:
                print('progress: %d/%d hits=%d' % (i+1, len(doms), len(hits)), flush=True)
    with open(HITS, 'w') as f:
        for h in hits:
            f.write('%s\t%s\t%s\n' % h)
    print('=== DONE: %d db backups ===' % len(hits), flush=True)

if __name__ == '__main__':
    main()
