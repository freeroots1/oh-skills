#!/usr/bin/env python3
"""yijingweb: find admin panel + login weak creds (亿景成品网站超市系统)"""
import urllib.request, re, gzip, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "zh-CN,zh;q=0.9", "Accept-Encoding": "gzip, deflate", "Connection": "keep-alive"}

def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        body = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            try: body = gzip.decompress(body)
            except Exception: pass
        return r.status, r.geturl(), body.decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(5000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

# common admin paths for 亿景/成品网站 systems
paths = ["/admin/", "/admin/login.php", "/admin/index.php", "/login.php", "/manage/",
         "/admin/login.html", "/houtai/", "/guanli/", "/system/", "/Admin/", "/adm/",
         "/admincp.php", "/houtai/index.php", "/admin/login.asp"]
for p in paths:
    code, final, body = fetch("http://www.yijingweb.com" + p)
    has_login = "password" in body.lower() or "用户名" in body or "登录" in body or "login" in body.lower()
    title = re.search(r"<title>([^<]*)</title>", body, re.I)
    print("%-22s code=%s size=%d login=%s %s" % (p, code, len(body), has_login,
          (title.group(1).strip()[:25] if title else "")), flush=True)
    time.sleep(2)
