#!/usr/bin/env python3
"""cap_probe.py - 探测30个ASP站验证码接口"""
import urllib.request, urllib.parse, ssl, re, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
SHELL = 'http://127.0.0.1:13080/proxy_t.php'

DOMAINS = ['www.aqsgpack.com', 'www.czdisar.com', 'www.east-tool.com',
           'www.hdhhg.com', 'www.jfjmjx.cn', 'www.marazziguide.com',
           'www.ntyq.cn', 'www.qbydby.com', 'www.qjsgf.com', 'www.xfscl.com',
           'www.xingyich.com.cn', 'www.xngl.com', 'www.yczhende.com',
           'www.zj-syfj.com', 'xwrubber.cn', 'xidipipe.com', 'webtex.cn',
           'szsadwj.com', 'wdzcz.com', 'lsks.org.cn', 'lspipesolutions.com',
           'skf-afl.com', 'smt66.com', 'huxhardware.com', 'aierpaike.com',
           'ecoair.cn', 'hbhmjc.com', 'sh-pump.com', 'puwall.cn', 'gdcq119.com']

def fetch_proxy(url, timeout=15):
    purl = 'http://127.0.0.1:13080/proxy_t.php?u=' + urllib.parse.quote(url, safe='')
    try:
        r = urllib.request.urlopen(urllib.request.Request(purl, headers=UA), timeout=timeout, context=ctx)
        b = r.read(50000)
        if b[:1] == b'[':
            m = re.match(rb'\[(\d+)\]', b)
            code = int(m.group(1))
            return code, b[m.end():]
        return r.status, b
    except Exception:
        return 0, b''

for dom in DOMAINS:
    # 检查登录页里验证码img的src
    st, b = fetch_proxy('http://' + dom + '/admin/login.asp')
    body = b.decode('gbk', 'ignore')
    cap_srcs = re.findall(r'<img[^>]*(?:code|Code|captcha|yzm)[^>]*src="([^"]+)"', body)
    if not cap_srcs:
        cap_srcs = re.findall(r'src="([^"]*(?:code|Code|captcha|yzm)[^"]*)"', body)
    print('%s: st=%d size=%d caps=%s' % (dom, st, len(b), cap_srcs[:2]), flush=True)
