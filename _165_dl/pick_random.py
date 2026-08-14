import random
random.seed(42)

with open('/tmp/all_4719_domains.txt') as f:
    all_domains = [l.strip() for l in f if l.strip()]

with open('/tmp/scanned_domains.txt') as f:
    scanned = set(l.strip() for l in f if l.strip())

adult_kw = ['porn','xxx','sex','av','tube','webcam','vod','jav','bdsm','hentai','nsfw','adult','fuck','pussy','gay','lesbian','escort','camgirl','onlyfans','milf','xvideo','xnxx','pornhub','redtube','youporn','xvideos','chat','roulette','dating','swinger','hookup','massage','ratxxx','guysroulette','nudecamboys','camboy']

clean = []
for d in all_domains:
    if d in scanned:
        continue
    low = d.lower()
    if any(kw in low for kw in adult_kw):
        continue
    clean.append(d)

print(f'Total clean untested: {len(clean)}')
picks = random.sample(clean, min(15, len(clean)))
for d in picks:
    print(d)
