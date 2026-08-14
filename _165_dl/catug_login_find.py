#!/usr/bin/env python3
"""catugbio: find login submit endpoint from JS"""
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

code, body = fetch("http://catugbio.com/admin/login.html")
print("login.html: %s size=%d" % (code, len(body)))
# find ajax/fetch urls
for m in re.finditer(r'(?:url|action)\s*[:=]\s*["\']([^"\']+)["\']', body):
    u = m.group(1)
    if "login" in u.lower() or "admin" in u.lower() or "api" in u.lower():
        print("URL:", u)
# script sources
for m in re.finditer(r'src=["\']([^"\']+\.js[^"\']*)["\']', body):
    print("JS:", m.group(1))
