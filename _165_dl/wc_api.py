#!/usr/bin/env python3
"""whcome.com API fuzz"""
import urllib.request, ssl, json
from concurrent.futures import ThreadPoolExecutor

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B = "http://whcome.com"

words = ["login","logout","user","users","admin","info","list","get","config","token",
         "auth","register","signup","forgot","reset","password","change","update",
         "upload","file","files","data","search","query","company","companies",
         "loginCheck","checkLogin","getUser","getInfo","getList","getData","index",
         "home","api","v1","v2","test","health","status","version","public","open"]

def check(path):
    try:
        req = urllib.request.Request(f"{B}/api/{path}", headers={"User-Agent":"Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=5, context=ctx)
        body = r.read().decode("utf-8","ignore")
        code = r.getcode()
        if code == 200 and len(body) < 500 and "501" not in body:
            return f"/api/{path}: {body[:80]}"
    except Exception as e:
        err = str(e)
        if "405" in err or "403" in err:
            return f"/api/{path}: {err[:40]}"
    return None

with ThreadPoolExecutor(16) as ex:
    for r in ex.map(check, words):
        if r:
            print(r, flush=True)
print("DONE")
