#!/usr/bin/env python3
"""ahbill.com deep: upload form location + admin paths + CMS detail"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
HOST = "http://ahbill.com"

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
print("home: %s size=%d" % (code, len(body)))
# find upload forms
print("=== upload forms ===")
for m in re.finditer(r'<form[^>]*>|<input[^>]*type=["\']file["\'][^>]*>|enctype=["\']multipart/form-data["\']', body, re.I):
    print("  ", m.group(0)[:120])
# all forms
print("=== all forms ===")
for m in re.finditer(r'<form[^>]*action=["\']([^"\']+)["\'][^>]*>', body, re.I):
    print("  form:", m.group(1)[:80])
# js includes (upload plugins?)
print("=== js hints ===")
for m in re.finditer(r'src=["\']([^"\']*(upload|kindeditor|ueditor|uploadify|webuploader)[^"\']*)["\']', body, re.I):
    print("  js:", m.group(1)[:80])

# admin paths
print("=== admin paths ===")
for p in ["/admin/", "/admin/login.php", "/admin/login", "/login.php", "/manage/",
          "/admin/index.php", "/houtai/", "/system/", "/administrator/"]:
    code, b = fetch(HOST + p)
    print("  %s: %s size=%d" % (p, code, len(b)))
