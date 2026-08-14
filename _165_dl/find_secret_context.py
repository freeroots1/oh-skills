#!/usr/bin/env python3
"""find_secret_context.py - 找secret密钥的上下文"""
import re

data = open('/tmp/db1.sql', encoding='utf-8', errors='ignore').read()

# 找 secret 的上下文
idx = data.find('m^Ss9N')
if idx >= 0:
    print('=== secret 上下文(前后200字符) ===')
    print(data[max(0,idx-200):idx+300])

print('\n=== 找WP认证密钥(AUTH_KEY等) ===')
for key in ['AUTH_KEY', 'SECURE_AUTH_KEY', 'LOGGED_IN_KEY', 'NONCE_KEY', 'AUTH_SALT', 'SECURE_AUTH_SALT', 'LOGGED_IN_SALT', 'NONCE_SALT']:
    m = re.search(r"define\(\s*'%s'\s*,\s*'([^']*)'" % key, data)
    if m:
        print('%s = %s' % (key, m.group(1)[:60]))

print('\n=== 找 wp_users 相关(可能遗漏) ===')
print('wp_users出现次数:', data.count('wp_users'))
print('user_pass出现次数:', data.count('user_pass'))
print('user_login出现次数:', data.count('user_login'))
