#!/usr/bin/env python3
"""check both sites' cloud-wangdun status with slow low-frequency requests"""
import urllib.request, re, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}

def check(url, tag):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=12)
        body = r.read().decode("utf-8", "ignore")
        blocked = "云网盾" in body
        print("%s: code=%s size=%d blocked=%s" % (tag, r.status, len(body), blocked), flush=True)
        return not blocked
    except urllib.error.HTTPError as e:
        body = e.read(3000).decode("utf-8", "ignore")
        print("%s: code=%s blocked=%s" % (tag, e.code, "云网盾" in body), flush=True)
        return False
    except Exception as ex:
        print("%s: ERR %s" % (tag, str(ex)[:40]), flush=True)
        return False

# wait for cooldown, then slow checks
print("waiting 60s for cooldown...", flush=True)
time.sleep(60)
check("http://yijingweb.com/webmall/detail.php?id=686", "yijing")
time.sleep(3)
check("http://zagroup.net/news.php?c=259", "zagroup")
