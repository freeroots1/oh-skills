#!/usr/bin/env python3
"""批量360搜索查收录"""
import urllib.request, ssl, re, time, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def check(domain):
    try:
        req = urllib.request.Request(f"https://www.so.com/s?q=site%3A{domain}", headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        h = urllib.request.urlopen(req, timeout=8, context=ctx).read().decode("utf-8","ignore")
        m = re.search(r'约(\d+)个网页被360搜索收录', h)
        if m:
            return f"收录{m.group(1)}页"
        if "的站点信息" in h:
            m2 = re.search(r'约(\d+)个网页', h)
            return f"收录{m2.group(1) if m2 else '?'}页"
        return "无数据"
    except Exception as e:
        return f"ERR:{str(e)[:20]}"

domains = sys.argv[1:]
for d in domains:
    print(f"{d}: {check(d)}", flush=True)
    time.sleep(0.8)
