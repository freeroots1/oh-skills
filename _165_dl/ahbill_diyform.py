#!/usr/bin/env python3
"""ahbill: diyform full form analysis + submit test"""
import urllib.request, urllib.parse, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://ahbill.com"

def fetch(url, timeout=10, data=None, headers=None):
    h = {**UA}
    if data: h["Content-Type"] = "application/x-www-form-urlencoded"
    if headers: h.update(headers)
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

# find the diyform form on home
code, final, body = fetch(HOST + "/")
i = body.find("/diyform/fcreate")
if i < 0:
    print("no diyform on home")
else:
    chunk = body[max(0,i-300):i+2000]
    print("=== diyform form chunk ===")
    print(chunk[:1500])
    # extract all fields with labels
    print("\n=== fields ===")
    for m in re.finditer(r'<(input|textarea|select)[^>]*>', chunk, re.I):
        tag = m.group(0)
        nm = re.search(r'name=["\']([^"\']+)["\']', tag, re.I)
        ty = re.search(r'type=["\']([^"\']+)["\']', tag, re.I)
        print("  %s name=%s type=%s" % (m.group(1), nm.group(1) if nm else "?", ty.group(1) if ty else "text"))
