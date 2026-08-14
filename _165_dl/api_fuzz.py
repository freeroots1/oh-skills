#!/usr/bin/env python3
"""API路径fuzz"""
import urllib.request, ssl, sys, concurrent.futures

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B = "https://101.201.82.174"

words = ["user","admin","login","index","info","config","base","list","get","set","add",
         "edit","del","delete","update","save","upload","file","img","image","chat",
         "msg","message","kefu","service","order","shop","merchant","agent","customer",
         "token","auth","pass","password","code","sms","phone","member","vip","pay",
         "money","stat","report","data","export","import","search","query","find",
         "home","main","menu","role","permission","group","log","sys","system","test",
         "api","open","public","common","comm","tool","help","version","health"]

def check(path):
    url = f"{B}/customer/api/{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=6, context=ctx)
        body = r.read().decode("utf-8","ignore")
        code = r.getcode()
        if code == 200 and len(body) > 10 and "404" not in body[:50]:
            return f"{path}: {body[:90]}"
    except Exception:
        pass
    return None

with concurrent.futures.ThreadPoolExecutor(16) as ex:
    for r in ex.map(check, words):
        if r:
            print(r, flush=True)
print("DONE")
