import hashlib, sys

target = "2d9d5942943a1323"

# First, try the most common passwords
for pwd in open("/tmp/rockyou.txt", "r", errors="ignore"):
    pwd = pwd.strip()
    if not pwd or len(pwd) < 3: continue
    md5 = hashlib.md5(pwd.encode()).hexdigest()
    if md5[8:24] == target:
        with open("/tmp/found_password.txt", "w") as f:
            f.write(f"FOUND! Password: {pwd}\n")
        print(f"FOUND: {pwd}")
        sys.exit(0)
print("Not found in rockyou")
