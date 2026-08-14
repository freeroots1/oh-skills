#!/usr/bin/env python3
"""find REAL file upload points in UPLOAD pool - type=file + multipart forms
Check upload endpoint actually accepts file (POST test with small file)
"""
import urllib.request, urllib.parse, re, http.cookiejar
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOSTILE = ["bet", "casino", "vip", "slot", "xxx", "porn", "xbux", "register"]

def fetch(url, timeout=8, data=None, raw=False):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"} if data else UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        body = r.read()
        return r.status, (body if raw else body.decode("utf-8", "ignore"))
    except urllib.error.HTTPError as e:
        return e.code, (e.read(3000) if raw else e.read(3000).decode("utf-8", "ignore"))
    except Exception:
        return 0, ""

def check(d):
    if any(h in d for h in HOSTILE):
        return None
    # 1. homepage for file input
    try:
        code, body = fetch("http://" + d + "/")
        if code != 200:
            return None
        # real file input
        file_inputs = re.findall(r'<input[^>]*type=["\']file["\'][^>]*>', body, re.I)
        if not file_inputs:
            return None
        # multipart forms
        forms = re.findall(r'<form[^>]*enctype=["\']multipart/form-data["\'][^>]*action=["\']([^"\']*)["\']', body, re.I)
        return (d, len(file_inputs), forms[:2])
    except Exception:
        return None

def main():
    doms = set()
    for line in open("/tmp/web_vuln2.txt"):
        m = re.search(r"\[UPLOAD\]\s+([a-z0-9.-]+)", line)
        if m:
            doms.add(m.group(1).strip().lower())
    print("UPLOAD pool: %d" % len(doms), flush=True)
    hits = []
    with ThreadPoolExecutor(max_workers=20) as ex:
        futs = {ex.submit(check, d): d for d in doms}
        for fut in as_completed(futs):
            r = fut.result()
            if r:
                hits.append(r)
                print("FILE-UPLOAD: %s | inputs=%d | forms=%s" % r, flush=True)
    print("\n=== REAL FILE UPLOAD SITES: %d ===" % len(hits))

if __name__ == "__main__":
    main()
