#!/usr/bin/env python3
"""phpMyAdmin SQL 执行器 — 登录后执行任意 SQL 返回结果
用法: python3 pma_exec.py <host[:port]> <pma_path> <user> <pwd> '<sql>'
"""
import urllib.request, http.cookiejar, re, sys, urllib.parse

def new_opener():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.addheaders = [("User-Agent", "Mozilla/5.0")]
    return op, cj

def main():
    host, path, user, pwd, sql = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    B = f"http://{host}{path}"
    op, cj = new_opener()
    r = op.open(B, timeout=10)
    html = r.read().decode("utf-8", "ignore")
    m = re.search(r'name="token" value="([a-f0-9]{32})"', html)
    if not m:
        print("NO_TOKEN"); return
    tok = m.group(1)
    # 登录
    data = f"pma_username={user}&pma_password={pwd}&server=1&token={tok}".encode()
    op.open(urllib.request.Request(B + "index.php", data=data), timeout=10).read()
    # 执行 SQL (import.php 方式)
    q = urllib.parse.urlencode({"token": tok, "sql_query": sql, "ajax_request": "true", "db": "mysql"})
    r = op.open(urllib.request.Request(B + "import.php?" + q, data=b""), timeout=15)
    body = r.read().decode("utf-8", "ignore")
    # 提取结果
    res = re.findall(r'<td[^>]*>([^<]{0,80})</td>', body)
    msgs = re.findall(r'class="success"[^>]*>(.*?)</div>', body, re.S)
    errs = re.findall(r'class="error"[^>]*>(.*?)</div>', body, re.S)
    print("SUCCESS" if "error" not in body.lower()[:2000] else "CHECK")
    for x in (msgs[:2] + res[:12]):
        x = x.strip()
        if x: print("  |", x[:100])
    for e in errs[:3]:
        print("  ERR:", e.strip()[:150])

if __name__ == "__main__":
    main()
