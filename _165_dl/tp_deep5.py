#!/usr/bin/env python3
"""tp_deep5.py - 提取模板里全部 {:url('...')} 控制器/方法名"""
import urllib.request, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BASE = "https://139.196.199.221"

def get(path):
    try:
        r = urllib.request.urlopen(urllib.request.Request(BASE + path, headers=UA), timeout=8, context=ctx)
        return r.status, r.read(150000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(150000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

templates = ["login/index.html", "index/index.html", "system/index.html", "order/index.html",
             "order/edit.html", "product/index.html", "goods/edit.html", "brand/index.html",
             "brand/edit.html", "banner/index.html", "log/index.html"]
urls = set()
for t in templates:
    st, b = get("/application/admin/view/%s" % t)
    if st != 200: continue
    for m in re.finditer(r"\{:url\('([^']+)'", b):
        urls.add(m.group(1))
    # 也抓 lay-data / 其他url
    for m in re.finditer(r"['\"]((?:admin|index|home)/[a-zA-Z]+/[a-zA-Z]+\.html)['\"]", b):
        urls.add(m.group(1))

print("=== 全部控制器/方法 ===", flush=True)
for u in sorted(urls):
    print("  %s" % u, flush=True)

# 汇总控制器->方法
print("\n=== 分组 ===", flush=True)
ctrl_methods = {}
for u in sorted(urls):
    parts = u.split("/")
    if len(parts) >= 2:
        c = parts[0]
        m = parts[1] if len(parts) > 1 else "?"
        ctrl_methods.setdefault(c, []).append(m)
for c, ms in sorted(ctrl_methods.items()):
    print("  %s: %s" % (c, ", ".join(sorted(set(ms)))), flush=True)
print("=== DONE ===", flush=True)
