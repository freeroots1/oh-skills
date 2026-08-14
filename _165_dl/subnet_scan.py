import json, glob, socket, subprocess, sys

# Phase 1: Extract all /24 subnets from known sites
subnets = set()
for f in glob.glob('/tmp/scan_results/*.json'):
    d = json.load(open(f))
    for ip in d.get('ips', []):
        parts = ip.split('.')
        if len(parts) == 4:
            subnets.add(parts[0] + '.' + parts[1] + '.' + parts[2])

print('Subnets from 88 sites:', len(subnets))

# Phase 2: Scan each subnet for IIS/ASP servers
found = []
for subnet in sorted(subnets):
    for host in range(1, 15):  # Scan .1 to .14
        ip = subnet + '.' + str(host)
        try:
            s = socket.socket()
            s.settimeout(1)
            if s.connect_ex((ip, 80)) == 0:
                s.close()
                r = subprocess.run(
                    ['curl', '-sk', '--connect-timeout', '3', '--max-time', '5',
                     'http://' + ip, '-o', '/dev/null', '-w',
                     '%{http_code}|%{size_download}|%{server}'],
                    capture_output=True, text=True, timeout=6)
                out = r.stdout.strip()
                parts_out = out.split('|')
                code = parts_out[0] if len(parts_out) > 0 else '000'
                size = parts_out[1] if len(parts_out) > 1 else '0'
                server = parts_out[2] if len(parts_out) > 2 else ''
                
                # Only keep sites with IIS/ASP or significant content
                is_iis = 'IIS' in server or 'Microsoft' in server
                has_content = int(size) > 1000 and code == '200'
                
                if is_iis or has_content:
                    print(ip + ' [' + server + '] ' + code + ':' + size)
                    found.append(ip)
                
                if len(found) >= 30:
                    break
        except:
            pass
    if len(found) >= 30:
        break

# Phase 3: For found IIS IPs, try to find domain names
print('\n=== IIS/ASP Servers ===')
for ip in found[:20]:
    try:
        r = subprocess.run(
            ['curl', '-sk', '--connect-timeout', '3', '--max-time', '5',
             'http://' + ip, '-o', '/dev/null', '-w', '%{server}'],
            capture_output=True, text=True, timeout=6)
        server = r.stdout.strip()
        if 'IIS' in server or 'Microsoft' in server:
            print(ip + ' -> ' + server)
    except:
        pass
