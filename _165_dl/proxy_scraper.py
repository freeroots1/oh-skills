#!/usr/bin/env python3
import subprocess, re, time, json, random

def scrape():
    proxies = set()
    sources = [
        'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=3000&country=all&ssl=all&anonymity=all',
        'https://www.proxy-list.download/api/v1/get?type=http',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
    ]
    for url in sources:
        try:
            r = subprocess.run(['curl','-sk','--connect-timeout','8','--max-time','12',url],
                             capture_output=True,text=True,timeout=15)
            for line in r.stdout.split('\n'):
                if re.match(r'\d+\.\d+\.\d+\.\d+:\d+', line.strip()):
                    proxies.add(line.strip())
        except: pass
    return list(proxies)

def test(proxy):
    try:
        r = subprocess.run(['curl','-sk','--connect-timeout','3','--max-time','5',
                           '-x',f'http://{proxy}','http://httpbin.org/ip'],
                          capture_output=True,text=True,timeout=6)
        return 'origin' in r.stdout
    except: return False

# Main
all_p = scrape()
print(f'Scraped: {len(all_p)} proxies')

working = []
for i, p in enumerate(all_p):
    if test(p):
        working.append(p)
        print(f'  [{i+1}/{len(all_p)}] OK: {p}')
    if len(working) >= 10: break

with open('/tmp/working_proxies.txt','w') as f:
    for p in working: f.write(p+'\n')

print(f'\nWorking: {len(working)}')
for p in working:
    print(f'  {p}')
