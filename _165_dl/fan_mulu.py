import requests

s = requests.Session()
s.get('http://bjhzsv.com/main/', timeout=10)
s.post('http://bjhzsv.com/main/a7chkuser.asp',
    data={'t1':'hermes','t2':'Hack888!','t3':'1234'},
    headers={'Referer':'http://bjhzsv.com/main/'}, timeout=10)

# Add articles
articles = [
    ['26', 'Article-1', 'keyword1,keyword2', 'Description text 1', 'Full article content here...'],
    ['27', 'Article-2', 'keyword3,keyword4', 'Description text 2', 'Full article content 2...'],
    ['28', 'Article-3', 'keyword5,keyword6', 'Description text 3', 'Full article content 3...'],
    ['29', 'Article-4', 'keyword7,keyword8', 'Description text 4', 'Full article content 4...'],
    ['30', 'Article-5', 'keyword9,keyword10', 'Description text 5', 'Full article content 5...'],
]

results = []
for cat_id, title, kw, desc, info in articles:
    r = s.post(
        'http://bjhzsv.com/main/news_in.asp?action=add',
        data={
            'D1': cat_id, 'title': title, 'keywords': kw,
            'description': desc, 'info': info,
            'year': '2026', 'month': '7', 'day': '30',
            'recommand': '1', 'author': 'admin', 'source': 'web',
            'B1': 'add'
        },
        timeout=10
    )
    text = r.content.decode('gbk', errors='replace')
    ok = 'VBScript' not in text and 'cdate' not in text.lower()
    results.append((cat_id, title, ok, text[:80]))
    print('%s %s: %s' % (cat_id, title, 'OK' if ok else 'ERR:' + text[:80]))

# Verify and show URLs
print('\n====== GENERATED SEO PAGES ======')
for cid in ['26','27','28','29','30']:
    r = requests.get('http://bjhzsv.com/class1_index.asp?id=' + cid, timeout=5)
    print('http://bjhzsv.com/class1_index.asp?id=%s | HTTP %d | %dB' % (cid, r.status_code, len(r.text)))
