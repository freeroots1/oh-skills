#!/usr/bin/env python3
"""3chan - extract EXACT form fields from submitThread in actions.js"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0"}

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(500000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

code, body = fetch("http://3chan.net/js/actions.js")
i = body.find("async function submitThread")
if i < 0:
    i = body.find("submitThread")
print("=== submitThread ===", flush=True)
print(body[i:i+1500] if i >= 0 else "not found", flush=True)
