import re
h = open('/tmp/kylin.html', encoding='utf-8', errors='ignore').read()
print('LEN', len(h))
# 打印所有script块
for m in re.finditer(r'<script[^>]*>(.*?)</script>', h, re.S):
    s = m.group(1).strip()
    if s and len(s) > 20:
        print('---SCRIPT---')
        print(s[:2000])
# 打印form
for m in re.finditer(r'<form[^>]*>', h):
    print('FORM:', m.group(0))
# 打印所有url/action引用
for m in re.finditer(r'["\'](/[^"\']*(?:login|Login|do|Do|check|Check)[^"\']*)["\']', h):
    print('URLREF:', m.group(1))
