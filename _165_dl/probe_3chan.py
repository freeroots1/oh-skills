#!/usr/bin/env python3
"""3chan.net - find post/upload endpoint (imageboard: /post, /new, board post pages)"""
import urllib.request, urllib.parse, re, http.cookiejar, uuid

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def get_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)), cj

def fetch(op, url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read(80000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)[:80]

op, cj = get_opener()
# explore common imageboard paths
for p in ["/", "/boards", "/post", "/new", "/upload", "/b/", "/b/1", "/index.html", "/boards.html"]:
    code, final, body = fetch(op, "http://3chan.net" + p)
    forms = re.findall(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*enctype=["\']multipart/form-data["\']', body, re.I)
    files = re.findall(r'type=["\']file["\']', body, re.I)
    print("%s: %s size=%d forms=%s files=%s" % (p, code, len(body), forms[:2], len(files)), flush=True)
    if forms or files:
        # show the form context
        idx = body.find('multipart')
        if idx > 0:
            print("  CONTEXT:", body[max(0,idx-200):idx+200].replace("\n", " ")[:300], flush=True)
