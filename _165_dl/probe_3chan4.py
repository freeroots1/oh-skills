#!/usr/bin/env python3
"""3chan - read actions.js apiPost function + api.php handling"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0"}

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(300000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

code, body = fetch("http://3chan.net/js/actions.js")
# find apiPost definition
i = body.find("function apiPost")
print("=== apiPost ===", flush=True)
print(body[i:i+600] if i > 0 else "not found", flush=True)
# find api calls
for m in re.finditer(r'api\.php[^"\']*', body):
    print("API CALL:", m.group(0), flush=True)
# all function defs with api
for m in re.finditer(r'async function (\w+)', body):
    print("FN:", m.group(1), flush=True)
