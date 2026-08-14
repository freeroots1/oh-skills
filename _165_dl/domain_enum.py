import socket, subprocess, sys

# Chinese machinery/construction company domain patterns
# Pattern: [city][keyword][suffix].com or [keyword][city].com.cn
prefixes = ['bj','sh','gz','sz','hz','nj','wh','cd','tj','qd','dl','xm','nb',
            'hd','jx','hb','hn','js','zj','sd','gd','fj','sc']
keywords = ['jx','jixie','machine','cnc','tool','mach','hardware','mold',
            'bearing','gear','pump','valve','motor','engine','robot',
            'jz','build','constr','steel','pipe','weld','fastener']
suffixes = ['com','com.cn','cn','net']

found = []
for prefix in prefixes[:10]:
    for kw in keywords[:10]:
        domain = prefix + kw + '.' + suffixes[0]
        try:
            ip = socket.gethostbyname(domain)
            if ip:
                # Quick HTTP check
                try:
                    r = subprocess.run(['curl','-sk','--connect-timeout','3','--max-time','5',
                        'http://'+domain,'-o','/dev/null','-w','%{http_code}'],
                        capture_output=True,text=True,timeout=6)
                    code = r.stdout.strip()
                    if code in ['200','301','302','403']:
                        print(domain + ' [' + ip + '] -> ' + code)
                        found.append(domain)
                except:
                    pass
        except:
            pass

print('Found:', len(found), 'sites')
