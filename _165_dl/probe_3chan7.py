#!/usr/bin/env python3
"""3chan - read utils.js apiFetch + all api.php callers for exact param names"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0"}

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(500000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

for js in ["/js/utils.js", "/js/views.js", "/js/routing.js", "/js/actions.js"]:
    code, body = fetch("http://3chan.net" + js)
    # apiFetch callers
    for m in re.finditer(r'apiFetch\(\{([^}]+)\}', body, re.DOTALL):
        print("%s apiFetch: {%s}" % (js, m.group(1).strip()[:150]), flush=True)
    for m in re.finditer(r'apiFetch\(\s*\{([^}]*)\}', body):
        pass
    # any 'action' assignments
    for m in re.finditer(r"['\"](?:action|act)['\"]\s*:\s*['\"]([^'\"]+)['\"]", body):
        print("%s ACTION: %s" % (js, m.group(1)), flush=True)
