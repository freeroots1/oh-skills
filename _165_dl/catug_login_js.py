#!/usr/bin/env python3
"""catugbio: read /static/login.js for login submit endpoint"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=10)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

code, body = fetch("http://catugbio.com/static/login.js")
print("login.js: %s size=%d" % (code, len(body)))
print(body[:2000])
