import subprocess, glob, json

domains = set()
for f in glob.glob('/tmp/scan_results/*.json'):
    d = json.load(open(f))
    domains.add(d['domain'])

targets = sorted(domains - {'silverplus-intl.com','gdrongda.com','bjhzsv.com'})

# Test each for: admin panel + default password
print('Testing default admin credentials on all sites...')
hits = []

for domain in targets:
    # Quick admin path test
    admin_paths = ['/admin','/admin/login','/login','/admin.php','/admin.aspx',
                   '/index.php/admin','/admin/login.php','/manage']
    
    for path in admin_paths:
        try:
            r = subprocess.run(['curl','-sk','--connect-timeout','2','--max-time','4',
                'http://'+domain+path,'-o','/dev/null','-w','%{http_code}:%{size_download}'],
                capture_output=True,text=True,timeout=5)
            parts = r.stdout.strip().split(':')
            if len(parts) >= 2:
                code = parts[0]
                size = int(parts[1])
                if code == '200' and size > 500 and size < 50000:
                    # Likely a real admin panel (not homepage-sized)
                    print(domain + path + ' -> ' + code + ' ' + str(size) + 'B')
                    hits.append((domain, path))
                    break
        except:
            pass
    if len(hits) >= 10:
        break

print('Found ' + str(len(hits)) + ' admin panels')
