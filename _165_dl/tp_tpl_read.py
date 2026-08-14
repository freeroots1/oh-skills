#!/usr/bin/env python3
"""tp_tpl_read.py - 读取上量后台全部模板内容, 提取接口/上传点"""
import urllib.request, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BASE = "https://139.196.199.221"

def get(path):
    try:
        r = urllib.request.urlopen(urllib.request.Request(BASE + path, headers=UA), timeout=8, context=ctx)
        return r.status, r.read(100000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(100000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

templates = [
    "/application/admin/view/login/index.html",
    "/application/admin/view/index/index.html",
    "/application/admin/view/system/index.html",
    "/application/admin/view/order/index.html",
    "/application/admin/view/order/edit.html",
    "/application/admin/view/product/index.html",
    "/application/admin/view/goods/edit.html",
    "/application/admin/view/brand/index.html",
    "/application/admin/view/brand/edit.html",
    "/application/admin/view/banner/index.html",
    "/application/admin/view/log/index.html",
]

all_urls = set()
for t in templates:
    st, b = get(t)
    if st != 200 or len(b) < 100:
        continue
    print("=== %s (size=%d) ===" % (t, len(b)), flush=True)
    # 提取所有URL模式
    for pat in [r'url\s*[:=]\s*["\']([^"\']+)["\']',
                r'action="([^"]+)"',
                r'href="([^"]*(?:html|php)[^"]*)"',
                r'data-url="([^"]+)"',
                r'data-action="([^"]+)"',
                r'src="([^"]*)"']:
        for m in re.finditer(pat, b, re.I):
            u = m.group(1)
            if len(u) > 2 and not u.startswith(("http", "//", "javascript", "data:")):
                all_urls.add(u)
    # 上传相关关键词
    for kw in ["upload", "Upload", "file", "File", "img", "pic", "icon", "ajax"]:
        for m in re.finditer(r'.{0,60}%s.{0,60}' % kw, b):
            s = m.group(0).strip()
            if "=" in s or ":" in s:
                pass
    # 表单字段
    for m in re.finditer(r'<input[^>]*name="([^"]+)"', b):
        pass

print("\n=== 汇总所有接口URL ===", flush=True)
for u in sorted(all_urls):
    print("  %s" % u, flush=True)
print("=== DONE ===", flush=True)
