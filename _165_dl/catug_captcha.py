#!/usr/bin/env python3
"""catugbio ThinkAdmin - captcha endpoint test + login with md5 chain"""
import urllib.request, urllib.parse, re, http.cookiejar, hashlib, json

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://catugbio.com"

def get_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)), cj

def fetch(op, url, timeout=10, data=None):
    h = {**UA}
    if data: h["Content-Type"] = "application/x-www-form-urlencoded"
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

op, cj = get_opener()
# 1. GET login page
code, body = fetch(op, HOST + "/admin/login.html")
print("login: %s size=%d" % (code, len(body)))
# find captcha url (data-captcha attr)
m = re.search(r'data-captcha="([^"]+)"', body)
cap_url = m.group(1) if m else "/admin/login.html"
print("captcha url:", cap_url)

# 2. GET captcha (ThinkAdmin: returns uniqid + image, sometimes code)
code, body = fetch(op, HOST + cap_url + "?type=captcha&token=captcha-token")
print("captcha resp: %s size=%d" % (code, len(body)))
print(body[:500])
