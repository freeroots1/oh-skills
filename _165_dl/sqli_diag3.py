#!/usr/bin/env python3
"""diagnose: what is the 4374B response on both sites"""
import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(8000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

print("=== yijingweb id=686 ===")
code, body = fetch("http://yijingweb.com/webmall/detail.php?id=686")
print("code=%s size=%d" % (code, len(body)))
print("title:", re.search(r"<title>([^<]*)</title>", body, re.I).group(1) if re.search(r"<title>([^<]*)</title>", body, re.I) else "NONE")
print("head:", body[:300].replace("\n", " "))

print("\n=== zagroup c=259 ===")
code, body = fetch("http://zagroup.net/news.php?c=259")
print("code=%s size=%d" % (code, len(body)))
print("title:", re.search(r"<title>([^<]*)</title>", body, re.I).group(1) if re.search(r"<title>([^<]*)</title>", body, re.I) else "NONE")
print("head:", body[:300].replace("\n", " "))

print("\n=== zagroup c=259' ===")
code, body = fetch("http://zagroup.net/news.php?c=259%27")
print("code=%s size=%d" % (code, len(body)))
m = re.search(r'MySQL server error</b>\s*:\s*<br>([^<]+)', body)
print("err:", m.group(1)[:200] if m else "NO ERROR")
print("head:", body[:300].replace("\n", " "))
