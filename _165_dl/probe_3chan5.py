#!/usr/bin/env python3
"""3chan - find apiPost helper (maybe in utils.js)"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0"}

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(300000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

for js in ["/js/utils.js", "/js/actions.js", "/js/config.js"]:
    code, body = fetch("http://3chan.net" + js)
    for kw in ["apiPost", "api.php", "FormData", "fetch("]:
        for m in list(re.finditer(re.escape(kw), body))[:5]:
            i = m.start()
            ctx = body[max(0,i-100):i+200].replace("\n", " ")
            print("%s | %s: ...%s..." % (js, kw, ctx[:250]), flush=True)
