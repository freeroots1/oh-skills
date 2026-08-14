#!/usr/bin/env python3
"""old_pool_scan.py - 老站池扫描: 存活+CMS指纹+后台路径
输入: /opt/msray/ALL_500.txt (域名列表)
输出: /tmp/old_scan_results.tsv
"""
import urllib.request, urllib.parse, ssl, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0'}

CMS_MARKS = [
    ("dedecms", ["dedecms", "织梦", "power by dede"]),
    ("wordpress", ["wp-content", "wp-includes", "wordpress"]),
    ("thinkphp", ["thinkphp", "think\\"]),
    ("pbootcms", ["pbootcms", "pb_lang"]),
    ("discuz", ["discuz", "powered by discuz"]),
    ("phpcms", ["phpcms"]),
    ("empirecms", ["empirecms", "ecms"]),
    ("ecshop", ["ecshop", "ectheme"]),
    ("shopex", ["shopex"]),
    ("asp/access", [".asp", ".mdb"]),
    ("aspnet", [".aspx", "asp.net"]),
    ("jsp", [".jsp", "java"]),
    ("php", ["php"]),
]

def fetch(url, timeout=7):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read(60000).decode('utf-8', 'ignore'), r.geturl(), r.headers.get('Server', '')
    except urllib.error.HTTPError as e:
        return e.code, e.read(60000).decode('utf-8', 'ignore'), e.geturl(), ''
    except Exception:
        return 0, '', '', ''

def scan(dom):
    st, b, fu, server = fetch('http://' + dom + '/')
    if st == 0 or st == 404:
        # 试https
        st, b, fu, server = fetch('https://' + dom + '/')
    if st == 0 or len(b) < 200:
        return None
    low = b.lower()
    marks = []
    for cms, keys in CMS_MARKS:
        for k in keys:
            if k.lower() in low:
                marks.append(cms)
                break
    # 版本特征
    ver = ''
    m = re.search(r'Powered by ([^<]{2,30})', b, re.I)
    if m:
        ver = m.group(1).strip()[:40]
    # 标题
    title = ''
    m = re.search(r'<title>([^<]{2,80})</title>', b, re.I)
    if m:
        title = m.group(1).strip()[:60]
    cms_str = ','.join(marks) if marks else 'unknown'
    return (dom, st, len(b), cms_str, server[:30], ver, title)

def main():
    doms = open('/opt/msray/ALL_500.txt').read().strip().split('\n')
    doms = [d.strip() for d in doms if d.strip() and not d.startswith('#')]
    print('targets: %d' % len(doms), flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=16) as ex:
        futs = {ex.submit(scan, d): d for d in doms}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception:
                r = None
            if r:
                results.append(r)
                print('\t'.join(str(x) for x in r), flush=True)
    with open('/tmp/old_scan_results.tsv', 'w') as f:
        for r in results:
            f.write('\t'.join(str(x) for x in r) + '\n')
    print('=== DONE: %d alive ===' % len(results), flush=True)

if __name__ == '__main__':
    main()
