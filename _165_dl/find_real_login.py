#!/usr/bin/env python3
"""find_real_login.py - 严格找真登录表单(password输入框) + 直接爆破
"""
import urllib.request, urllib.parse, ssl, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def fetch(url, timeout=8, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
            headers={**UA, "Content-Type": "application/x-www-form-urlencoded"} if data else UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return r.status, r.read(80000).decode("utf-8", "ignore"), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(80000).decode("utf-8", "ignore"), e.geturl()
    except Exception:
        return 0, "", ""

def check_target(dom, path):
    url = "http://" + dom + path
    st, body, _ = fetch(url)
    if st != 200 or len(body) < 800:
        return None
    # 严格判定: 有 password 输入框
    has_pw = bool(re.search(r'<input[^>]*type=["\']password["\']', body, re.I)) or 'type="password"' in body
    if not has_pw:
        return None
    # 表单字段
    fields = re.findall(r'<input[^>]*name="([^"]+)"[^>]*>', body, re.I)
    action = re.search(r'<form[^>]*action="([^"]*)"', body, re.I)
    form_action = action.group(1) if action else path
    if not form_action.startswith("http"):
        base = "http://" + dom
        form_action = base + (form_action if form_action.startswith("/") else "/" + form_action)
    return {"dom": dom, "path": path, "fields": fields, "action": form_action,
            "pw_field": next((f for f in fields if "pass" in f.lower() or "pwd" in f.lower()), "password")}

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "/tmp/admin_hits6.txt"
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
            if size < 1000:
                continue
            if dom in seen:
                continue
            seen.add(dom)
            cands.append((dom, path))
    print("unique domains: %d" % len(cands), flush=True)

    logins = []
    with ThreadPoolExecutor(max_workers=20) as ex:
        futs = [ex.submit(check_target, d, p) for d, p in cands]
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception:
                r = None
            if r:
                logins.append(r)
                print("LOGIN: %s\t%s\tfields=%s\taction=%s" % (r["dom"], r["path"], r["fields"][:8], r["action"][:60]), flush=True)

    with open("/tmp/real_logins.tsv", "w") as f:
        for r in logins:
            f.write("%s\t%s\t%s\t%s\n" % (r["dom"], r["path"], "|".join(r["fields"]), r["action"]))
    print("=== DONE: %d real login forms ===" % len(logins), flush=True)

if __name__ == "__main__":
    main()
