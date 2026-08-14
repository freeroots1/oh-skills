import hashlib, sys

target = "2d9d5942943a1323"
target999 = "79dca16741891333"

# Check p100.txt passwords against both hashes
with open("/tmp/p100.txt", "r", errors="ignore") as f:
    for line in f:
        pwd = line.strip()
        if not pwd:
            continue
        md5 = hashlib.md5(pwd.encode()).hexdigest()
        mid = md5[8:24]
        if mid == target:
            print(f"FOUND! admin password: {pwd}")
            sys.exit(0)
        if mid == target999:
            print(f"FOUND! admin999 password: {pwd}")
            sys.exit(0)
        # Also try lowercase
        md5_lower = hashlib.md5(pwd.lower().encode()).hexdigest()
        mid_lower = md5_lower[8:24]
        if mid_lower == target:
            print(f"FOUND! admin password (lower): {pwd.lower()}")
            sys.exit(0)
        if mid_lower == target999:
            print(f"FOUND! admin999 password (lower): {pwd.lower()}")
            sys.exit(0)

# Also check big_pass.txt
with open("/tmp/big_pass.txt", "r", errors="ignore") as f:
    for line in f:
        pwd = line.strip()
        if not pwd:
            continue
        md5 = hashlib.md5(pwd.encode()).hexdigest()
        mid = md5[8:24]
        if mid == target:
            print(f"FOUND! admin password: {pwd}")
            sys.exit(0)
        if mid == target999:
            print(f"FOUND! admin999 password: {pwd}")
            sys.exit(0)

print("Not found in p100/big_pass lists", file=sys.stderr)
# Show what some hashes look like
for t in ["CNKuai2024", "CNKuai", "P@ssw0rd", "Server2024", "TJZR"]:
    m = hashlib.md5(t.encode()).hexdigest()
    print(f"  {t}: {m[8:24]}")
