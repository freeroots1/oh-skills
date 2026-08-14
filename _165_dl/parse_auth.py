import re
h = open('/tmp/auth113.html', encoding='utf-8', errors='ignore').read()
i = h.find('<form')
seg = h[i:i+4000]
for m in re.finditer(r'<input[^>]*>', seg):
    print(m.group(0)[:250])
print('---names---')
for m in re.finditer(r'name="([^"]+)"', seg):
    print('name:', m.group(1))
