#!/usr/bin/env python3
"""dede_vuln_batch.py - DedeCMS批量漏洞检测(637站)
检测: 后台路径/版本泄露/前台已知漏洞点
"""
import urllib.request, ssl, socket, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

socket.setdefaulttimeout(6)
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0'

CHECKS = [
    ("dede-login", "/dede/login.php"),
    ("dede-index", "/dede/index.php"),
    ("ver.txt", "/data/admin/ver.txt"),
    ("plus-search", "/plus/search.php"),
    ("plus-download", "/plus/download.php"),
    ("plus-flink", "/plus/flink.php"),
    ("member-index", "/member/index.php"),
    ("uploads", "/uploads/"),
]

def fetch(url, timeout=5):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, len(r.read())
    except urllib.error.HTTPError as e:
        return e.code, 0
    except Exception:
        return 0, 0

def scan(dom):
    res = []
    for name, path in CHECKS:
        code, size = fetch("http://%s%s" % (dom, path))
        if code == 200 and size > 100:
            res.append((name, path, size))
    return dom, res

def main():
    doms = [l.strip() for l in open('/tmp/dede_targets.txt') if l.strip()]
    print('DedeCMS targets: %d, 12 threads' % len(doms), flush=True)
    results = {}
    done = 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(scan, d): d for d in doms}
        for fut in as_completed(futs):
            done += 1
            dom, res = fut.result()
            if res:
                results[dom] = res
                print('HIT: %s %s' % (dom, ' '.join('%s(%d)' % (n, s) for n, p, s in res[:4])), flush=True)
            if done % 100 == 0:
                print('progress: %d/%d hits=%d' % (done, len(doms), len(results)), flush=True)
    with open('/tmp/dede_vuln_hits.tsv', 'w') as f:
        for dom, res in results.items():
            for n, p, s in res:
                f.write('%s\t%s\t%s\t%d\n' % (dom, n, p, s))
    print('[done] %d dede hits' % len(results), flush=True)

if __name__ == '__main__':
    main()
