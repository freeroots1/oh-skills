#!/usr/bin/env python3
"""cms_probe.py - 批量探测国产CMS (TP/Pboot/Dede)"""
import urllib.request, ssl, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

def probe(dom):
    hits = []
    try:
        req = urllib.request.Request('http://' + dom, headers=UA)
        r = urllib.request.urlopen(req, timeout=5, context=ctx)
        b = r.read(50000).decode('utf-8', 'ignore')
        low = b.lower()
        if 'thinkphp' in low or 'think' in low and 'framework' in low:
            hits.append('tp')
        if 'pbootcms' in low or 'pb_lang' in low:
            hits.append('pboot')
        if 'dedecms' in low or 'dede' in low:
            hits.append('dede')
        if 'phpstudy' in low:
            hits.append('phpstudy')
    except Exception:
        pass
    return hits

def main():
    doms = open('/tmp/all_backend_doms.txt').read().strip().split('\n')
    print('scanning %d domains' % len(doms), flush=True)
    results = []
    for d in doms:
        h = probe(d)
        if h:
            results.append((d, ','.join(h)))
            print('%s: %s' % (d, ','.join(h)), flush=True)
    with open('/tmp/cms_hits.txt', 'w') as f:
        for d, c in results:
            f.write('%s\t%s\n' % (d, c))
    print('=== DONE: %d CMS hits ===' % len(results), flush=True)

if __name__ == '__main__':
    main()
