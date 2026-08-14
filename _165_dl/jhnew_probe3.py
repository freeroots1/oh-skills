#!/usr/bin/env python3
"""jhnew: inspect 405 body + find real login endpoint"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://jhnew.com"

def get_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)), cj

def fetch(op, url, timeout=10, data=None, referer=None):
    h = {**UA}
    if data: h["Content-Type"] = "application/x-www-form-urlencoded"
    if referer: h["Referer"] = referer
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

op, cj = get_opener()
# GET the full admin page (login form context)
code, final, body = fetch(op, HOST + "/admin/")
print("admin/ size=%d" % len(body))
# full form html
i = body.find("<form")
print("FORM CONTEXT:", body[max(0,i-200):i+800] if i > 0 else "no form")

# POST to login.php raw and see 405 body
import http.client
try:
    conn = http.client.HTTPConnection("jhnew.com", timeout=10)
    body_data = urllib.parse.urlencode({"userid": "admin", "pwd": "admin", "dopost": "login"})
    conn.request("POST", "/admin/login.php", body=body_data,
                 headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": UA["User-Agent"]})
    r = conn.getresponse()
    print("POST login.php: %s size=%d body=%s" % (r.status, len(r.read()), r.read()[:100]))
except Exception as e:
    print("conn err:", e)
