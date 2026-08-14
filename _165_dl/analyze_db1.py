#!/usr/bin/env python3
"""analyze_db1.py - 分析8.6MB WordPress数据库dump, 提取敏感信息"""
import re

data = open('/tmp/db1.sql', encoding='utf-8', errors='ignore').read()

print('=== 文件大小 ===')
print(len(data), 'chars')

print('\n=== siteurl/home/admin_email ===')
for key in ['siteurl', 'home', 'admin_email', 'blogname', 'blogdescription']:
    # WordPress dump格式: (1,'siteurl','http://...','yes')
    for m in re.finditer(r"\(\d+,'%s','([^']*)'" % key, data):
        print('%s = %s' % (key, m.group(1)))

print('\n=== 找所有URL(域名) ===')
urls = set(re.findall(r'https?://[a-zA-Z0-9.-]+\.[a-z]{2,}', data))
for u in sorted(urls)[:30]:
    print(' ', u)

print('\n=== 找API密钥/secret/token ===')
for m in re.finditer(r"'(mailgun|sendgrid|stripe|paypal|google|recaptcha|smtp|api|secret|token|key|password)[^']*',\s*'([^']{8,120})'", data, re.I):
    print(' ', m.group(1), '=', m.group(2))

print('\n=== 找邮箱(排除图片命名) ===')
emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}', data))
real = [e for e in emails if not e.endswith('.jpg') and not e.endswith('.png') and not re.search(r'@\d+x\d+', e)]
for e in sorted(real)[:30]:
    print(' ', e)

print('\n=== wp_options里所有option_name ===')
opts = set(re.findall(r"\(\d+,'([a-z0-9_]+)','", data))
for o in sorted(opts):
    print(' ', o)
