import urllib.request, urllib.parse, io
import http.cookiejar
from PIL import Image
import pytesseract

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Get captcha
resp = opener.open('http://bjhzsv.com/main/inc/code.asp', timeout=10)
cap_data = resp.read()
print(f'Captcha size: {len(cap_data)}, Cookies: {len(list(cj))}')

# Get cookies
for c in cj:
    print(f'  Cookie: {c.name}={c.value}')

# OCR
img = Image.open(io.BytesIO(cap_data))
img = img.convert('L')
img = img.point(lambda x: 0 if x < 200 else 255)
code = pytesseract.image_to_string(img, config='--psm 8').strip().replace(' ', '').lower()
print(f'Captcha code: "{code}"')

# Login
if len(code) >= 3:
    data = urllib.parse.urlencode({'t1': 'admin', 't2': '2d9d5942943a1323', 't3': code}).encode()
    resp = opener.open('http://bjhzsv.com/main/a7chkuser.asp', data, timeout=10)
    body = resp.read().decode('gb2312', errors='replace')
    print(f'Login response ({len(body)} bytes):')
    print(f'  Contains alert: {"alert" in body}')
    print(f'  Contains location.href: {"location.href" in body}')
    print(f'  Contains 验证码错误: {"验证码错误" in body}')
    print(f'  First 200 chars: {body[:200]}')

# Now access index.asp with the session
resp2 = opener.open('http://bjhzsv.com/main/index.asp', timeout=10)
body2 = resp2.read().decode('gb2312', errors='replace')
print(f'\nindex.asp ({len(body2)} bytes):')
print(f'  Contains login form: {"t1" in body2 and "t2" in body2}')
print(f'  Contains admin content: {"管理" in body2 and "t1" not in body2}')
print(f'  First 300 chars: {body2[:300]}')

# Also try accessing with the raw cookie value
# Maybe the login sets a session but index.asp needs a different check
import re
# Check for any hidden fields or session indicators
hidden = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*>', body2, re.I)
print(f'Hidden fields: {hidden}')
