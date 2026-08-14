import subprocess, json, re, time

# Load blacklist
blacklist = set()
try:
    with open('/tmp/blacklist_domains.txt') as f:
        for line in f: blacklist.add(line.strip())
except: pass

print('Blacklist:', len(blacklist))

# Phase 1: CommonCrawl collection
CC = 'https://index.commoncrawl.org/CC-MAIN-2024-30-index'
new_domains = set()

# Multiple searches
searches = [
    'url=*.com.cn/*&filter=mime:text/html&output=json&limit=100',
    'url=*.cn/*&filter=encoding:gb2312&output=json&limit=50',
    'url=*/news.asp*&filter=mime:text/html&output=json&limit=30',
    'url=*/products.asp*&filter=mime:text/html&output=json&limit=30',
]

for query in searches:
    try:
        r = subprocess.run(['curl', '-sk', '--connect-timeout', '20',
            CC + '?' + query], capture_output=True, text=True, timeout=25)
        for line in r.stdout.strip().split('\n'):
            try:
                d = json.loads(line)
                m = re.search(r'https?://([^/]+)', d['url'])
                if m:
                    domain = m.group(1)
                    if domain not in blacklist:
                        new_domains.add(domain)
            except: pass
    except: pass

print('New domains from CommonCrawl:', len(new_domains))

# Phase 2: Live check
live = []
for domain in list(new_domains)[:50]:
    try:
        r = subprocess.run(['curl', '-sk', '--connect-timeout', '3', '--max-time', '5',
            'http://' + domain, '-o', '/dev/null', '-w', '%{http_code}:%{size_download}:%{server}'],
            capture_output=True, text=True, timeout=6)
        parts = r.stdout.strip().split(':')
        code = parts[0]
        size = int(parts[1]) if len(parts) > 1 else 0
        server = parts[2] if len(parts) > 2 else ''
        if code in ['200','301','302'] and size > 1000:
            live.append((domain, code, size, server))
            print(domain + ' [' + code + '] ' + str(size) + 'B ' + server[:30])
    except: pass

print('Live domains:', len(live))

# Phase 3: Save to target list
with open('/tmp/new_targets.txt', 'w') as f:
    for d, _, _, _ in live:
        f.write(d + '\n')
