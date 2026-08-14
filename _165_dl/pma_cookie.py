#!/usr/bin/env python3
"""phpMyAdmin cookie状态检查"""
import urllib.request, http.cookiejar, ssl, re

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "http://39.105.7.208:8980/phpmyadmin"

def dump_cookies(tag):
    print(f"[{tag}] cookies:", [(c.name, c.value[:20]) for c in cj], flush=True)

# 1. 访问首页
r = op.open(f"{B}/", timeout=10)
html = r.read().decode("utf-8","ignore")
token = re.search(r'name="token" value="([a-f0-9]{32})"', html)
token = token.group(1) if token else None
print(f"首页 len={len(html)} token={token[:16] if token else None}", flush=True)
dump_cookies("首页后")

# 2. 登录
data = f"pma_username=root&pma_password=root&server=1&token={token}".encode()
try:
    r = op.open(urllib.request.Request(f"{B}/index.php", data=data), timeout=10)
    body = r.read()
    print(f"登录POST: code={r.getcode()} len={len(body)} url={r.geturl()}", flush=True)
    dump_cookies("登录后")
except Exception as e:
    print(f"登录ERR: {str(e)[:60]}", flush=True)

# 3. 登录后访问index.php
try:
    r = op.open(f"{B}/index.php", timeout=10)
    body = r.read().decode("utf-8","ignore")
    print(f"登录后访问index: len={len(body)}", flush=True)
    if "logout" in body: print("  >>> 已登录状态!", flush=True)
    if "Cannot log in" in body: print("  >>> 未登录", flush=True)
    t = re.search(r"<title>([^<]*)</title>", body)
    print(f"  标题: {t.group(1) if t else '?'}", flush=True)
except Exception as e:
    print(f"ERR: {str(e)[:60]}", flush=True)
