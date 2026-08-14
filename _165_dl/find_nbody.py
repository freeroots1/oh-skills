#!/usr/bin/env python3
import re
t3 = open('/tmp/kir_sn_1043.html', encoding='gbk', errors='ignore').read()
# find spic filename context
idx = t3.find('BACBCAB7')
print('=== spic context (1043) ===')
print(t3[max(0,idx-300):idx+300].replace('\r','').replace('\n',' '))
print()
# find nbody/content region: look for the actual news body area
# page seems to render company intro; find where news content would be
for kw in ['公司简介', '新闻', 'nbody', 'content', 'body']:
    for m in re.finditer(kw, t3):
        i = m.start()
        print('--- %s at %d ---' % (kw, i))
        print(' '.join(t3[max(0,i-100):i+200].split())[:300])
        break
