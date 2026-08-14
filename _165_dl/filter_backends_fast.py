#!/usr/bin/env python3
"""filter_backends_fast.py - 并发筛选真实后台 + CMS指纹
用法: python3 filter_backends_fast.py [src] [min_size] [threads]
"""
import urllib.request, ssl, re, sys, os
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

CMS_MARKS = [
    ("dedecms", ["dedecms", "power by dede", "织梦", "DedeCMS"]),
    ("wordpress", ["wp-login", "wordpress", "wp-content", "wp-includes"]),
    ("thinkphp", ["thinkphp", "think\\", "ThinkPHP"]),
    ("pbootcms", ["pbootcms", "pb_lang", "pboot"]),
    ("discuz", ["discuz", "powered by discuz"]),
    ("empirecms", ["empirecms", "ecms", "帝国"]),
    ("phpcms", ["phpcms", "phpcmsv9"]),
    ("ecshop", ["ecshop", "ectheme"]),
    ("z-blog", ["z-blog", "zb_users"]),
    ("typecho", ["typecho"]),
    ("greencms", ["greencms", "green_cms"]),
    ("asp/access", [".asp", ".mdb", "access"]),
]

def fetch(url, timeout=7):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read(50000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(50000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

def check(dom, path):
    url = "http://" + dom + path
    st, body = fetch(url)
    if st != 200 or len(body) < 500:
        return None
    low = body.lower()
    marks = []
    for cms, keys in CMS_MARKS:
        for k in keys:
            if k.lower() in low:
                marks.append(cms)
                break
    has_login = any(k in low for k in ["password", "type=\"password\"", "login", "登录", "密码", "sign in", "user_login"])
    has_admin = any(k in low for k in ["dashboard", "logout", "退出", "管理", "后台", "控制台", "系统设置", "内容管理", "用户管理"])
    if has_login or has_admin:
        cms_str = ",".join(marks) if marks else "unknown"
        return (dom, path, cms_str, len(body), "LOGIN" if has_login else "ADMIN")
    return None

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "/tmp/admin_hits6.txt"
    min_size = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
    threads = int(sys.argv[3]) if len(sys.argv) > 3 else 16

    cands = []
    seen = set()
    with open(src) as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 3:
                continue
            dom, path, resp = parts[0], parts[1], parts[2]
            if not resp.startswith("200:"):
                continue
            size = int(resp.split(":")[1])
            if size < min_size:
                continue
            key = dom + path
            if key in seen:
                continue
            seen.add(key)
            cands.append((dom, path))

    print("candidates: %d threads=%d" % (len(cands), threads), flush=True)
    results = []
    done_doms = set()
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = [ex.submit(check, d, p) for d, p in cands]
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception:
                r = None
            if r and r[0] not in done_doms:
                done_doms.add(r[0])
                results.append(r)
                print("\t".join(str(x) for x in r), flush=True)

    with open("/tmp/real_backends.tsv", "w") as f:
        for r in results:
            f.write("\t".join(str(x) for x in r) + "\n")
    print("=== DONE: %d real backends ===" % len(results), flush=True)

if __name__ == "__main__":
    main()
