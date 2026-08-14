#!/usr/bin/env python3
"""zileijg: formPost details - action, upload fields, VIEWSTATE"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://zileijg.com"

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

code, body = fetch(HOST + "/")
# formPost context
i = body.find("formPost")
print("=== formPost context ===")
print(body[max(0,i-200):i+800] if i > 0 else "not found")
# find file inputs
for m in re.finditer(r'<input[^>]*type=["\']file["\'][^>]*>', body, re.I):
    print("FILE INPUT:", m.group(0)[:150])
# VIEWSTATE (ASP.NET)
vs = re.findall(r'__VIEWSTATE[^>]*value="([^"]*)"', body)
print("VIEWSTATE len:", len(vs[0]) if vs else 0)
# all forms with actions
for m in re.finditer(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>', body, re.I):
    print("FORM ACTION:", m.group(1))
