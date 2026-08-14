#!/usr/bin/env python3
"""jhnew: DedeCMS login page full form + captcha field"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://jhnew.com"

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

code, body = fetch(HOST + "/admin/login.php")
print("login.php: %s size=%d" % (code, len(body)))
# all fields
for m in re.finditer(r'<input[^>]*>', body):
    print("  ", m.group(0)[:130])
# captcha img?
for m in re.finditer(r'(<img[^>]*captcha[^>]*>|<img[^>]*vdcode[^>]*>)', body, re.I):
    print("CAPTCHA:", m.group(0)[:100])
# form
fm = re.search(r'<form[^>]*>', body, re.I)
print("form:", fm.group(0)[:100] if fm else "?")
