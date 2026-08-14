import json, glob, subprocess

domains = set()
for f in glob.glob('/tmp/scan_results/*.json'):
    d = json.load(open(f))
    domains.add(d['domain'])

skip = {'silverplus-intl.com', 'gdrongda.com', 'bjhzsv.com'}
targets = sorted(domains - skip)

results = []
for domain in targets:
    try:
        r = subprocess.run(['curl', '-sk', '--connect-timeout', '3', '--max-time', '5',
            'http://' + domain, '-o', '/dev/null', '-w', '%{http_code}:%{size_download}'],
            capture_output=True, text=True, timeout=6)
        code_size = r.stdout.strip()
        if not code_size.startswith('000'):
            code = code_size.split(':')[0]
            size = code_size.split(':')[1] if ':' in code_size else '0'
            if int(size) > 500:
                print(domain + ' [' + code + ' ' + size + 'B]')
                results.append(domain)
    except:
        pass

print('Live: ' + str(len(results)) + '/' + str(len(targets)))
