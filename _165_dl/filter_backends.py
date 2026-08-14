#!/usr/bin/env python3
"""filter_backends.py - 从admin_hits6筛选真实后台 + CMS指纹分类
输出: /tmp/real_backends.tsv (域名\t路径\tCMS\t特征)
"""
import urllib.request, ssl, re, sys, os

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

CMS_MARKS = {
    "dedecms": ["dedecms", "power by dede", "织梦", "/dede/", "DedeCMS"],
    "wordpress": ["wp-login", "wordpress", "wp-content"],
    "thinkphp": ["thinkphp", "think\\", "think\\", "ThinkPHP"],
    "pbootcms": ["pbootcms", "pb_lang", "pboot"],
    "discuz": ["discuz", "powered by discuz", "uchome"],
    "empirecms": ["empirecms", "ecms", "帝国"],
    "phpcms": ["phpcms", "phpcmsv9"],
    "shopex": ["shopex", "ectouch"],
    "ecshop": ["ecshop", "ectheme"],
    "z-blog": ["z-blog", "zb_users"],
    "typecho": ["typecho"],
    "greenCMS": ["greencms", "green_cms"],
    "asp/access": [".asp", "Access", "MDB"],
    "generic-php": ["php", "login", "password", "admin"],
}

def fetch(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read(80000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(80000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""

def fingerprint(body):
    low = body.lower()
    marks = []
    for cms, keys in CMS_MARKS.items():
        for k in keys:
            if k.lower() in low:
                marks.append(cms)
                break
    return marks

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "/tmp/admin_hits6.txt"
    min_size = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    out = []
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
            out.append((dom, path, size))

    print("candidates: %d" % len(out), flush=True)
    results = []
    for dom, path, size in out:
        # 只测每个域名的第一个路径(同域名多路径重复)
        if dom in [r[0] for r in results]:
            continue
        url = "http://" + dom + path
        st, body = fetch(url)
        if st != 200 or len(body) < 500:
            continue
        marks = fingerprint(body)
        has_login = any(k in body.lower() for k in ["password", "login", "登录", "密码", "sign in", "user_login"])
        has_admin = any(k in body.lower() for k in ["dashboard", "logout", "退出", "管理", "后台", "控制台", "系统设置", "内容管理"])
        cms = ",".join(marks) if marks else "unknown"
        # 判定: 有登录表单 或 有后台特征
        if has_login or has_admin:
            results.append((dom, path, cms, size, "LOGIN" if has_login else "ADMIN", len(body)))
            print("%s\t%s\t%s\t%d\t%s\t%d" % (dom, path, cms, size, "LOGIN" if has_login else "ADMIN", len(body)), flush=True)

    # 保存
    with open("/tmp/real_backends.tsv", "w") as f:
        for r in results:
            f.write("\t".join(str(x) for x in r) + "\n")
    print("=== DONE: %d real backends ===" % len(results), flush=True)

if __name__ == "__main__":
    main()
