#!/usr/bin/env python3
"""scan_cms_backends.py - 扫2571个已确认CMS站的后台 (15线程低负载)
"""
import urllib.request, ssl, socket, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict

socket.setdefaulttimeout(5)
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0'
PATHS = ["/admin/login.php", "/admin/index.php", "/admin/", "/admin.php", "/login.php",
         "/manage/", "/admin/login.asp", "/admin/index.asp", "/houtai/", "/admin/login", "/dede/"]

def fetch(url, timeout=4):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, len(r.read())
    except urllib.error.HTTPError as e:
        return e.code, 0
    except Exception:
        return 0, 0

def scan(dom):
    hits = []
    for p in PATHS:
        code, size = fetch("http://%s%s" % (dom, p))
        if code == 200 and 200 < size < 80000:
            hits.append((dom, p, size))
    return hits

def main():
    doms = [l.strip() for l in open('/tmp/cms_doms_v2.txt') if l.strip()]
    print('targets: %d, 15 threads' % len(doms), flush=True)
    all_hits = []
    done = 0
    with ThreadPoolExecutor(max_workers=15) as ex:
        futs = {ex.submit(scan, d): d for d in doms}
        for fut in as_completed(futs):
            done += 1
            hs = fut.result()
            if hs:
                all_hits.extend(hs)
            if done % 300 == 0:
                print('progress: %d/%d hits=%d' % (done, len(doms), len(all_hits)), flush=True)
    dc = Counter(h[0] for h in all_hits)
    real = [h for h in all_hits if dc[h[0]] < 8]
    by_dom = defaultdict(list)
    for d, p, s in real:
        by_dom[d].append((p, s))
    with open('/tmp/cms_backends.tsv', 'w') as f:
        for d, plist in sorted(by_dom.items(), key=lambda x: len(x[1])):
            for p, s in plist[:3]:
                f.write('%s\t%s\t%d\n' % (d, p, s))
    print('[done] %d domains, %d hit-paths -> cms_backends.tsv' % (len(by_dom), len(real)), flush=True)
    for d, plist in sorted(by_dom.items(), key=lambda x: len(x[1]))[:40]:
        print('BACKEND: %s %s' % (d, ' '.join('%s(%d)' % (p, s) for p, s in plist[:3])), flush=True)

if __name__ == '__main__':
    main()
