#!/usr/bin/env python3
"""test cloud-wangdun bypass: different UA / referer / cookies"""
import urllib.request, re, time

def fetch(url, ua, timeout=12):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(8000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
    "Baiduspider/2.0",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
]
print("=== yijingweb id=686 with different UAs ===")
for ua in UAS:
    code, body = fetch("http://yijingweb.com/webmall/detail.php?id=686", ua)
    blocked = "云网盾" in body
    title = re.search(r"<title>([^<]*)</title>", body, re.I)
    print("  %-45s code=%s size=%d blocked=%s %s" % (ua[:42], code, len(body), blocked, title.group(1)[:20] if title else ""))
    time.sleep(1)
