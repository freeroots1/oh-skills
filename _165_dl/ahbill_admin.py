#!/usr/bin/env python3
"""ahbill: /admin/ content + diyform fields + upload test"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
HOST = "http://ahbill.com"

def fetch(url, timeout=10, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

# /admin/ content
code, body = fetch(HOST + "/admin/")
print("=== /admin/ ===")
print("code=%s size=%d" % (code, len(body)))
title = re.search(r"<title>([^<]*)</title>", body, re.I)
print("title:", title.group(1) if title else "?")
# login form?
if "password" in body.lower() or "login" in body.lower():
    print("HAS LOGIN FORM")
for m in re.finditer(r'<form[^>]*>', body, re.I):
    print("  form:", m.group(0)[:120])
for m in re.finditer(r'<input[^>]*name=["\']([^"\']+)["\']', body, re.I):
    print("  input:", m.group(1))

# diyform page - find the form with file field
code, body = fetch(HOST + "/")
# find form fields around /diyform/fcreate
i = body.find("/diyform/fcreate")
if i > 0:
    print("\n=== diyform form fields ===")
    chunk = body[max(0,i-100):i+1500]
    for m in re.finditer(r'name=["\']([^"\']+)["\']', chunk):
        print("  field:", m.group(1))
    for m in re.finditer(r'type=["\']([^"\']+)["\']', chunk):
        print("  type:", m.group(1))
