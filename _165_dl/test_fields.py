import urllib.request, sys
for fn in ["title","Title","TITLE","biaoti","bt","subject","heading","topic","name","Name"]:
    data = fn + "=TestArticle&content=test&author=admin&day=29&month=7&year=2026"
    req = urllib.request.Request("http://bjhzsv.com/main/news_in.asp?action=add", data.encode(), headers={"User-Agent":"Mozilla/5.0"})
    try:
        body = urllib.request.urlopen(req, timeout=10).read()
        if b"\xc3\xbb\xd3\xd0\xd0\xb4\xc8\xeb\xb1\xea\xcc\xe2" in body:
            print(f"NO_TITLE: {fn}")
        elif b"\xc0\xe0\xd0\xcd\xb2\xbb\xc6\xa5\xc5\xe4" in body:
            print(f"TYPE_MISMATCH: {fn}")
        elif b"\xb3\xc9\xb9\xa6" in body:
            print(f"SUCCESS: {fn}")
        else:
            print(f"OTHER: {fn} -> {body[:80]}")
    except Exception as e:
        print(f"ERR: {fn} -> {e}")
