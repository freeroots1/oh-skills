#!/usr/bin/env python3
"""catugbio: parse captcha JSON for uniqid + save image for OCR"""
import urllib.request, json, base64, re

UA = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=10)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)

code, body = fetch("http://catugbio.com/admin/login/captcha")
print("resp: %s" % body[:300])
try:
    j = json.loads(body)
    data = j.get("data", {})
    print("keys:", list(data.keys()))
    print("uniqid:", data.get("uniqid"))
    print("code field:", data.get("code"))
    img_b64 = data.get("image", "")
    if img_b64.startswith("data:image"):
        img_b64 = img_b64.split(",", 1)[1]
    if img_b64:
        img = base64.b64decode(img_b64)
        open("/tmp/catug_captcha.png", "wb").write(img)
        print("saved captcha: %d bytes" % len(img))
except Exception as e:
    print("parse err:", e)
