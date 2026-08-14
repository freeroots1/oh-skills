import json, urllib.request

url = 'https://api.github.com/repos/TideSec/TscanPlus/releases'
req = urllib.request.Request(url, headers={'Accept': 'application/vnd.github+json'})
resp = urllib.request.urlopen(req, timeout=20)
releases = json.loads(resp.read())

for rel in releases[:5]:
    print(f'{rel["tag_name"]} ({rel["published_at"][:10]})')
    for a in rel.get('assets', []):
        print(f'  {a["name"]} ({a["size"]} bytes)')
    print()
