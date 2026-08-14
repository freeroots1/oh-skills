#!/usr/bin/env python3
import urllib.request, urllib.parse, re, http.cookiejar
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "*/*"}
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def fetch(url, data=None):
    try:
        req = urllib.request.Request(url, data=data.encode() if data else None, headers={**UA,"Content-Type":"application/x-www-form-urlencoded"})
        r = op.open(req, timeout=10)
        return r.status, r.geturl(), r.read().decode('utf-8','ignore')
    except urllib.error.HTTPError as e:
        return e.code, url, e.read().decode('utf-8','ignore')
    except Exception as ex:
        return 0, url, str(ex)

code, final, body = fetch('http://h5jz.net/wp-login.php')
print('1) GET wp-login:', code, final, 'len', len(body))
login_url = final if final.startswith('http') else 'http://h5jz.net/wp-login.php'
payload = {'log':'admin','pwd':'12345678','wp-submit':'Log In','redirect_to':re.sub(r'https?://','http://',login_url).replace('wp-login.php','wp-admin/'),'testcookie':'1'}
code2, final2, resp = fetch(login_url, data=urllib.parse.urlencode(payload))
print('2) POST login:', code2, final2, 'len', len(resp))
admin_url = final2 if 'wp-admin' in final2 else re.sub(r'wp-login\.php.*','wp-admin/',login_url)
print('   admin_url:', admin_url)
code3, final3, body3 = fetch(admin_url)
print('3) GET admin:', code3, final3, 'len', len(body3))
for kw in ['dashboard','dashicons','wp-admin-bar','user_login','wp-login']:
    print('   contains %s:' % kw, kw in body3.lower())
