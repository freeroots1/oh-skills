import hashlib, sys

targets = {
    "admin": "2d9d5942943a1323",
    "admin999": "79dca16741891333",
    "hacker": "51b042435a457d9d",
    "hack5": "a6afbbcbf8be7668",
    "shell": "623ed667ccda39e9",
}

# Load rockyou and check ALL hashes
count = 0
with open("/tmp/rockyou.txt", "r", errors="ignore") as f:
    for line in f:
        pwd = line.strip()
        if not pwd or len(pwd) < 3:
            continue
        md5 = hashlib.md5(pwd.encode()).hexdigest()
        mid = md5[8:24]
        found = []
        for name, target in targets.items():
            if mid == target:
                found.append(name)
        if found:
            for name in found:
                print(f"FOUND! {name} password: {pwd}")
                del targets[name]
            if not targets:
                sys.exit(0)
        count += 1
        if count % 500000 == 0:
            remaining = ", ".join(targets.keys())
            print(f"Progress: {count/1000000:.1f}M - remaining: {remaining}", file=sys.stderr)

if targets:
    remaining = ", ".join(targets.keys())
    print(f"Rockyou exhausted. Remaining: {remaining}", file=sys.stderr)
    sys.exit(1)
