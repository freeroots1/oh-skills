#!/usr/bin/env python3
"""zagroup: full error page dump to understand query structure"""
import urllib.request, re, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(8000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

code, body = fetch("http://zagroup.net/news.php?c=259%27")
# full error block
i = body.find("MySQL Query Error")
print("=== error block ===")
print(body[i:i+1500] if i > 0 else body[:1500])
print("\n=== tail of page ===")
print(body[-500:])
