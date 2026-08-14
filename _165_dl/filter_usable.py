#!/usr/bin/env python3
"""filter_usable.py - 从43k域名筛出可用目标
标准: 存活(HTTP 200) + 有后台路径命中 + 排除泛解析
输出: /tmp/usable_targets.tsv (域名\t后台路径\t大小)
"""
import urllib.request, ssl, socket, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter

socket.setdefaulttimeout(6)
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0'
PATHS = ["/admin/login.php", "/admin/index.php", "/admin/", "/admin.php", "/login.php",
         "/manage/", "/admin/login.asp", "/admin/index.asp", "/houtai/", "/admin/login", "/dede/"]

def fetch(url, timeout=4):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        body = r.read()
        return r.status, len(body)
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
    doms = []
    with open('/opt/msray/collect_clean.txt') as f:
        doms = [l.strip().lower() for l in f if l.strip()]
    doms = list(dict.fromkeys(doms))
    print('input: %d domains, 11 paths, 50 threads' % len(doms), flush=True)
    all_hits = []
    done = 0
    with ThreadPoolExecutor(max_workers=50) as ex:
        futs = {ex.submit(scan, d): d for d in doms}
        for fut in as_completed(futs):
            done += 1
            hs = fut.result()
            if hs:
                all_hits.extend(hs)
            if done % 2000 == 0:
                print('progress: %d/%d hits=%d' % (done, len(doms), len(all_hits)), flush=True)
    # 排除泛解析(catch-all: 单域名>=8路径全中)
    dc = Counter(h[0] for h in all_hits)
    real = [h for h in all_hits if dc[h[0]] < 8]
    # 按命中数排序(1-2个路径=真实后台; 3-7=可能泛解析但保留)
    from collections import defaultdict
    by_dom = defaultdict(list)
    for d, p, s in real:
        by_dom[d].append((p, s))
    # 输出: 单路径后台优先
    with open('/tmp/usable_targets.tsv', 'w') as f:
        for d, plist in sorted(by_dom.items(), key=lambda x: len(x[1])):
            for p, s in plist[:3]:
                f.write('%s\t%s\t%d\n' % (d, p, s))
    print('[done] %d domains with %d hit-paths -> usable_targets.tsv' % (len(by_dom), len(real)), flush=True)
    # 打印前30
    for d, plist in sorted(by_dom.items(), key=lambda x: len(x[1]))[:30]:
        print('USABLE: %s %s' % (d, ' '.join('%s(%d)' % (p, s) for p, s in plist[:3])), flush=True)

if __name__ == '__main__':
    main()
