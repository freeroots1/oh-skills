#!/usr/bin/env python3
"""gz - dump login page full HTML to find captcha + form"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

code, body = fetch("http://gz-dichuan.com/index.php?m=admin&c=login&a=index")
print("code=%s size=%d" % (code, len(body)))
print(body)
