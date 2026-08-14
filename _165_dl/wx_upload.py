#!/usr/bin/env python3
"""wxiajin EmpireCMS 会员上传点探测"""
import urllib.request, http.cookiejar, urllib.parse, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]
B = "https://wxiajin.com"

def login():
    r = op.open(f"{B}/e/member/login/", timeout=10); r.read()
    data = urllib.parse.urlencode({"enews":"login","username":"hunter888","password":"hunter123"}).encode()
    req = urllib.request.Request(f"{B}/e/member/doaction.php", data=data, headers={"Referer":f"{B}/e/member/login/"})
    r = op.open(req, timeout=10)
    body = r.read().decode("gbk","ignore")
    return "登录成功" if "鎴愬姛" in body or "success" in body.lower() else body[:80]

def get(url):
    try:
        r = op.open(f"{B}{url}", timeout=10)
        return r.read().decode("gbk","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:50]}"

if __name__ == "__main__":
    print("登录:", login()[:50], flush=True)
    # 会员中心常见页面
    pages = ["/e/member/cp/", "/e/member/cp/EditInfo.php", "/e/member/cp/EditFace.php",
             "/e/member/cp/ChangeInfo.php", "/e/member/edit/info/", "/e/member/cp/index.php?action=edit",
             "/e/member/cp/?action=edit", "/e/member/uploadface.php", "/e/member/cp/uploadface.php"]
    for p in pages:
        b = get(p)
        if b.startswith("ERR"):
            print(f"[ERR] {p}: {b[:40]}", flush=True)
            continue
        has_upload = any(k in b.lower() for k in ["upload", "file", "头像", "上传", "face", "enctype"])
        has_edit = any(k in b for k in ["修改", "编辑", "edit"])
        print(f"[{len(b)}B] {p} upload={has_upload} edit={has_edit}", flush=True)
        if has_upload:
            # 打印表单
            for m in re.findall(r"<(?:form|input)[^>]*>", b)[:20]:
                if "file" in m.lower() or "upload" in m.lower() or "action" in m.lower():
                    print(f"   FORM: {m[:150]}", flush=True)
