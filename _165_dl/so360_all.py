#!/usr/bin/env python3
"""批量360收录查询 - 全部域名"""
import urllib.request, ssl, re, time, sys, http.cookiejar

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def check(domain):
    try:
        cj = http.cookiejar.CookieJar()
        op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
        op.addheaders = [("User-Agent","Mozilla/5.0 (Windows NT 10.0; Win64; x64)"),
                         ("Referer","https://www.so.com/")]
        try:
            op.open("https://www.so.com/", timeout=5).read()
        except Exception:
            pass
        h = op.open(f"https://www.so.com/s?q=site%3A{domain}", timeout=8).read().decode("utf-8","ignore")
        m = re.search(r'约(\d+)个网页被360搜索收录', h)
        if m:
            return int(m.group(1))
        if "未找到相关搜索结果" in h:
            return 0
        if "的站点信息" in h:
            m2 = re.search(r'约(\d+)个网页', h)
            return int(m2.group(1)) if m2 else 0
        return -1
    except Exception:
        return -2

# 从文件读域名列表
domains = [l.strip() for l in open("/tmp/all_domains.txt") if l.strip()]
hits = []
for d in domains:
    r = check(d)
    if r > 0:
        hits.append((d, r))
        print(f"!!! {d}: 收录{r}页", flush=True)
    time.sleep(0.7)
print(f"DONE total={len(domains)} 有收录={len(hits)}", flush=True)
