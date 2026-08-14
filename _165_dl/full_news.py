import requests

s = requests.Session()
s.get("http://bjhzsv.com/main/", timeout=10)
s.post("http://bjhzsv.com/main/a7chkuser.asp",
    data={"t1": "hermes", "t2": "Hack888!", "t3": "1234"},
    headers={"Referer": "http://bjhzsv.com/main/"}, timeout=10)

# Get full news_add.asp
print("=" * 60)
print("FULL news_add.asp")
print("=" * 60)
r = s.get("http://bjhzsv.com/main/news_add.asp", timeout=10)
t = r.content.decode("gb2312", errors="replace")
print(t[:3000])

print("\n" + "=" * 60)
print("FULL news_add2.asp")
print("=" * 60)
r = s.get("http://bjhzsv.com/main/news_add2.asp", timeout=10)
t = r.content.decode("gb2312", errors="replace")
print(t[:3000])
