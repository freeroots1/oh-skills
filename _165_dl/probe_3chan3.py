#!/usr/bin/env python3
"""3chan - read actions.js for upload API endpoint"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(200000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)[:80]

for js in ["/js/actions.js", "/js/config.js", "/js/routing.js"]:
    code, body = fetch("http://3chan.net" + js)
    print("=== %s (%s, %dB) ===" % (js, code, len(body)), flush=True)
    # find endpoints
    for m in re.finditer(r'(?:fetch|axios|post|put)\(["\']([^"\']+)["\']', body, re.I):
        print("  ENDPOINT:", m.group(1), flush=True)
    for m in re.finditer(r'(?:url|endpoint|api)\s*[:=]\s*["\']([^"\']+)["\']', body, re.I):
        print("  URL:", m.group(1), flush=True)
    # upload function context
    for kw in ["upload", "post", "file"]:
        for m in list(re.finditer(kw, body, re.I))[:4]:
            i = m.start()
            print("  %s: ...%s..." % (kw, body[max(0,i-60):i+80].replace("\n", " ")[:130]), flush=True)
