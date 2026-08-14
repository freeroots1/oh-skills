#!/usr/bin/env python3
"""batch_form_analyze.py - 批量分析30个ASP站表单(通过form_analyze.php)"""
import urllib.request, urllib.parse, ssl, re, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
FA = 'http://127.0.0.1:13080/form_analyze.php'

DOMAINS = ['www.aqsgpack.com', 'www.czdisar.com', 'www.east-tool.com',
           'www.hdhhg.com', 'www.jfjmjx.cn', 'www.marazziguide.com',
           'www.ntyq.cn', 'www.qbydby.com', 'www.qjsgf.com', 'www.xfscl.com',
           'www.xingyich.com.cn', 'www.xngl.com', 'www.yczhende.com',
           'www.zj-syfj.com', 'xwrubber.cn', 'xidipipe.com', 'webtex.cn',
           'szsadwj.com', 'wdzcz.com', 'lsks.org.cn', 'lspipesolutions.com',
           'skf-afl.com', 'smt66.com', 'huxhardware.com', 'aierpaike.com',
           'ecoair.cn', 'hbhmjc.com', 'sh-pump.com', 'puwall.cn', 'gdcq119.com']

def fetch(url, timeout=25):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.read(40000).decode('utf-8', 'ignore')
    except Exception as e:
        return 'ERR:' + repr(e)[:60]

for dom in DOMAINS:
    out = fetch(FA + '?d=' + urllib.parse.quote(dom))
    # 提取LEN
    m = re.search(r'LEN:(\d+)\|', out)
    if not m:
        print('%s: ERR %s' % (dom, out[:60].replace(chr(10), ' ')), flush=True)
        continue
    body = out[m.end():]
    # 字段
    fields = re.findall(r'name="([^"]+)"', body)
    # 验证码img
    cap = re.findall(r'src="([^"]*(?:code|Code|captcha|yzm)[^"]*)"', body)
    # action
    action = re.findall(r'action="([^"]*)"', body)
    print('%s: len=%s fields=%s cap=%s action=%s' % (dom, m.group(1), fields[:6], cap[:2], action[:2]), flush=True)
