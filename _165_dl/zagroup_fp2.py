#!/usr/bin/env python3
"""zagroup: CMS fingerprint + FTP user enumeration + server headers"""
import urllib.request, re, gzip

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "zh-CN,zh;q=0.9", "Accept-Encoding": "gzip, deflate"}

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        body = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            try: body = gzip.decompress(body)
            except Exception: pass
        return r.status, r.headers, body.decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, {}, str(ex)

# server headers
code, headers, body = fetch("http://zagroup.net/")
print("=== headers ===")
for k, v in headers.items():
    if k.lower() in ("server", "x-powered-by", "x-aspnet-version", "set-cookie"):
        print("  %s: %s" % (k, v))
print("=== home ===")
print("code=%s size=%d" % (code, len(body)))
title = re.search(r"<title>([^<]*)</title>", body, re.I)
print("title:", title.group(1).strip()[:40] if title else "?")
# CMS hints
for kw in ["wordpress", "dedecms", "phpcms", "asp.net", "aspx", "discuz", "phpwind", "ecshop", "帝国", "织梦"]:
    if kw.lower() in body.lower():
        print("HINT:", kw)
# dynamic urls
dyn = re.findall(r'([\w./-]+\.(?:php|asp|aspx|html)\?[\w]+=[\w]+)', body)
print("dynamic:", dyn[:5])

# login pages
print("=== login paths ===")
for p in ["/admin/", "/admin/login.php", "/login.php", "/manage/", "/admin/login.asp", "/admin/index.asp"]:
    code, h, b = fetch("http://zagroup.net" + p)
    has_login = "password" in b.lower() or "用户名" in b or "login" in b.lower()
    print("  %s: code=%s size=%d login=%s" % (p, code, len(b), has_login))
