import json, os, glob, re, socket, subprocess, sys

ip_re = re.compile(r'^(?:\d{1,3}\.){3}\d{1,3}$')

ips = set()
hostnames = set()
for f in glob.glob('/tmp/scan_results/*.json'):
    try:
        with open(f) as fh:
            data = json.load(fh)
        for item in data.get('ips', []):
            item = item.strip().rstrip('.')
            if ip_re.match(item):
                ips.add(item)
            else:
                hostnames.add(item)
    except: pass

# Resolve hostnames
resolved = {}
for h in sorted(hostnames):
    try:
        result = socket.getaddrinfo(h, None)
        for r in result:
            addr = r[4][0]
            if ip_re.match(addr):
                resolved[h] = addr
                break
    except Exception as e:
        resolved[h] = f'FAILED: {e}'

# Print resolved
for h in sorted(hostnames):
    print(f'{h} -> {resolved.get(h, "UNKNOWN")}')

# Merge all IPs
all_ips = set(ips)
for h, ip in resolved.items():
    if ip_re.match(ip):
        all_ips.add(ip)

print(f'\nTotal unique IPs (after DNS resolution): {len(all_ips)}')

# Write IP list to file
with open('/tmp/all_ips.txt', 'w') as f:
    for ip in sorted(all_ips):
        f.write(ip + '\n')

print('IPs written to /tmp/all_ips.txt')
