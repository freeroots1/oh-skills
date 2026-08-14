#!/usr/bin/env python3
"""Mailu单次登录测试"""
import urllib.request, http.cookiejar, ssl

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B = "http://51xyg.com"

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]

# 先拿登录页
r = op.open(f"{B}/sso/login", timeout=8)
print("GET /sso/login:", r.getcode(), r.geturl(), flush=True)

# 提交admin/admin
data = "email=admin&pw=admin&submitAdmin=Sign+in+Admin&pwned=-1".encode()
r = op.open(urllib.request.Request(f"{B}/sso/login", data=data), timeout=8)
body = r.read().decode("utf-8","ignore")
print("POST:", r.getcode(), r.geturl(), flush=True)
print("len:", len(body), flush=True)
# 找错误信息
import re
msgs = re.findall(r'class="[^"]*(?:error|alert|warning)[^"]*"[^>]*>(.{0,100})', body, re.S)
print("错误消息:", [re.sub(r'<[^>]+>','',m).strip()[:60] for m in msgs[:3]], flush=True)
# 找alert
alerts = re.findall(r'(?:alert|flash|message)[^>]*>(.{0,100})', body, re.S)
print("alerts:", [re.sub(r'<[^>]+>','',a).strip()[:60] for a in alerts[:3]], flush=True)
