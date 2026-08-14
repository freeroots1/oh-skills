#!/usr/bin/env python3
"""3chan - inspect file input context + JS for upload endpoint"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(200000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)[:80]

code, body = fetch("http://3chan.net/")
# file input context
for m in re.finditer(r'<input[^>]*type=["\']file["\'][^>]*>', body, re.I):
    i = m.start()
    print("FILE INPUT CONTEXT:", body[max(0,i-300):i+100].replace("\n", " ")[:350], "\n", flush=True)
# forms anywhere
forms = re.findall(r'<form[^>]*>', body, re.I)
print("forms:", forms[:5], flush=True)
# JS files for upload logic
scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', body, re.I)
print("scripts:", scripts[:8], flush=True)
# look for upload/api keywords
for kw in ["upload", "api", "post", "submit", "enctype"]:
    idxs = [m.start() for m in re.finditer(kw, body, re.I)][:3]
    for i in idxs:
        print("KW %s:", kw, body[max(0,i-80):i+80].replace("\n", " ")[:150], flush=True)
