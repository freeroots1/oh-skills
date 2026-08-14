import re
h = open('/tmp/sl.html', encoding='utf-8', errors='ignore').read()
print('LEN', len(h))
for m in re.finditer(r'<script[^>]*>(.*?)</script>', h, re.S):
    s = m.group(1).strip()
    if s and len(s) > 30:
        print('---SCRIPT---')
        print(s[:3000])
for m in re.finditer(r'<img[^>]*>', h):
    print('IMG:', m.group(0)[:200])
for m in re.finditer(r'<form[^>]*>', h):
    print('FORM:', m.group(0))
