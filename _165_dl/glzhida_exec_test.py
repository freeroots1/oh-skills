#!/usr/bin/env python3
"""glzhida_exec_test.py - 测glzhida.com哪些php能执行
源码泄露标志: 响应以<?php开头; 执行标志: 响应非<?php开头且>500字节
"""
import urllib.request, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
BASE = 'http://glzhida.com'

FILES = ['/index.php', '/plus/list.php', '/plus/search.php', '/plus/download.php', '/plus/click.php',
         '/plus/view.php', '/plus/count.php', '/plus/feedback.php', '/plus/recommend.php',
         '/plus/flink.php', '/plus/mytag_js.php', '/include/common.inc.php', '/include/vdimgck.php',
         '/gladmin/login.php', '/gladmin/index.php', '/member/index.php', '/tags.php',
         '/search.php', '/uploads/index.php', '/xmlrpc.php', '/404.php']

def fetch(url, timeout=8):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        body = r.read(5000)
        return r.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000)
    except Exception:
        return 0, b''

for f in FILES:
    st, body = fetch(BASE + f)
    head = body[:30]
    if body.startswith(b'<?php'):
        kind = 'SOURCE-LEAK'
    elif st == 200 and len(body) > 500:
        kind = 'EXECUTES(%d)' % len(body)
    elif st == 404:
        kind = '404'
    else:
        kind = 'other(%d,%d)' % (st, len(body))
    print('%s -> %s' % (f, kind), flush=True)
