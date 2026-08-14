import hashlib, sys, subprocess, os

target = "2d9d5942943a1323"
count = 0
batch_size = 10000

def check(pwd):
    if len(pwd) < 3:
        return False
    md5 = hashlib.md5(pwd.encode()).hexdigest()
    return md5[8:24] == target

# Use hashcat --stdout with mask attack for 6-char lowercase
masks = ["?l?l?l?l?l?l", "?l?l?l?l?l?d", "?l?l?l?l?d?d", "?d?d?d?d?d?d",
         "?l?l?l?l?l?l?l", "?l?l?l?l?l?l?d", "?l?l?l?l?l?d?d",
         "?l?l?l?l?d?d?d", "?d?d?d?d?d?d?d"]

# First try hashcat for short alphanumeric
for mask in masks:
    print(f"Trying mask: {mask}", file=sys.stderr)
    try:
        proc = subprocess.Popen(
            ["hashcat", "--stdout", "-a", "3", mask],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        for line in proc.stdout:
            pwd = line.strip()
            if check(pwd):
                print(f"FOUND! Password: {pwd}")
                proc.terminate()
                sys.exit(0)
            count += 1
            if count % 100000 == 0:
                print(f"  Progress: {count/1000000:.1f}M", file=sys.stderr)
        proc.wait()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

# Also try hashcat with dictionary + rules
print("Trying dictionary + rules...", file=sys.stderr)
try:
    proc = subprocess.Popen(
        ["hashcat", "--stdout", "-a", "0", "/tmp/rockyou.txt", "-r", "/usr/share/hashcat/rules/best64.rule"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    for line in proc.stdout:
        pwd = line.strip()
        if check(pwd):
            print(f"FOUND! Password: {pwd}")
            proc.terminate()
            sys.exit(0)
        count += 1
        if count % 100000 == 0:
            print(f"  Rule progress: {count/1000000:.1f}M", file=sys.stderr)
    proc.wait()
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)

print(f"Total checked: {count}", file=sys.stderr)
print("Not found", file=sys.stderr)
