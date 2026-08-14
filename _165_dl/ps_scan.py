#!/usr/bin/env python3
"""60.191.221.198 并发路径扫描"""
import urllib.request, ssl, concurrent.futures

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B = "http://60.191.221.198:8980"

paths = ["/phpStudy/","/bbs/","/upload/","/uploads/","/data/","/install/","/demo/","/test/",
         "/tools/","/backup/","/sql/","/db/","/files/","/file/","/images/","/img/",
         "/include/","/inc/","/lib/","/cache/","/temp/","/logs/","/api/","/app/",
         "/shop/","/cms/","/dede/","/e/","/wp-admin/","/administrator/","/admin.php",
         "/login.php","/index.asp","/default.asp","/conn.asp","/x.php","/hack.php",
         "/cmd.php","/manager/","/manage/","/web/","/main/","/houtai/","/ht/",
         "/zhan/","/home/","/wap/","/m/","/mobile/","/portal/","/news/","/product/",
         "/about/","/contact/","/company/","/gongsi/","/chanpin/","/xinwen/",
         "/admin/","/manage/index.asp","/admin/index.asp","/data/backup/","/database/",
         "/mysql/","/myadmin/","/pma/","/phpmyadmin2/","/adminer.php","/phpinfo.php",
         "/info.php","/test.php","/l.php","/i.php","/php.php","/shell.php","/1.php"]

def check(p):
    try:
        req = urllib.request.Request(B+p, headers={"User-Agent":"Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=5, context=ctx)
        body = r.read()
        if r.getcode() == 200 and len(body) > 50 and b"404" not in body[:100] and b"<html" in body[:500]:
            return f"{p}: {r.getcode()} {len(body)}B"
    except Exception:
        pass
    return None

with concurrent.futures.ThreadPoolExecutor(20) as ex:
    for r in ex.map(check, paths):
        if r:
            print(r, flush=True)
print("DONE")
