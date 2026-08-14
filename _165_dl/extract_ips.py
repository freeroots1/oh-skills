import json, os, glob, re, socket

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

print(f'Valid IPs: {len(ips)}')
print(f'Hostnames to resolve: {len(hostnames)}')
print('---VALID_IPS---')
for ip in sorted(ips):
    print(ip)
print('---HOSTNAMES---')
for h in sorted(hostnames):
    print(h)
