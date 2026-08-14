#!/usr/bin/env python3
"""gz-dichuan login with captcha retry loop"""
import urllib.request, urllib.parse, re, http.cookiejar, base64, subprocess, sys

HOST = "http://gz-dichuan.com"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def ocr(img_bytes):
    b64 = base64.b64encode(img_bytes).decode()
    code = "import ddddocr,base64; o=ddddocr.DdddOcr(show_ad=False); print(o.classification(base64.b64decode('%s')))" % b64
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=20, cwd="/tmp")
    return r.stdout.decode().strip()

for attempt in range(8):
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    def fetch(url, data=None, timeout=12, headers=None):
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
        print("attempt %d: OCR=%s resp=%s" % (attempt, cap_text, rt[:80]))
        if "登录成功" in rt or "success" in rt.lower() or '"status":1' in rt:
            print("LOGIN OK!")
            # fetch adddrugs
            code, final, body = fetch(HOST + "/index.php?m=admin&c=goods&a=adddrugs",
                                      headers={"Referer": HOST + "/index.php?m=admin&c=index&a=index"})
            bt = body.decode("utf-8", "ignore")
            open("/tmp/gz_adddrugs.html", "w").write(bt)
            print("adddrugs:", code, final, "size", len(bt))
            for m in re.finditer(r'<input[^>]*type=["\']file["\'][^>]*>', bt, re.I):
                print("FILE INPUT:", m.group(0)[:150])
            for m in re.finditer(r'(ue\.|UEDITOR|ueditor|kindeditor|uploadify|webuploader)', bt, re.I):
                i = m.start()
                print("UPLOAD-REF:", bt[max(0,i-60):i+80].replace("\n", " ")[:140])
            break
    except Exception as e:
        print("attempt %d error: %s" % (attempt, e))
