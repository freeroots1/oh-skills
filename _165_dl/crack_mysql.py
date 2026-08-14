import sys

def mysql_old_password(password):
    nr = 1345345333
    add = 7
    nr2 = 0x12345671
    for c in password:
        if c == " " or c == "\t":
            continue
        byte = ord(c)
        nr ^= (((nr & 63) + add) * byte) + (nr << 8)
        nr2 += (nr2 << 8) ^ nr
        add += byte
    nr &= 0x7fffffff
    nr2 &= 0x7fffffff
    return "%08lx%08lx" % (nr, nr2)

targets = {"2d9d5942943a1323": "admin", "79dca16741891333": "admin999"}
found = {}

with open("/tmp/rockyou.txt", "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f):
        pwd = line.strip()
        if not pwd:
            continue
        h = mysql_old_password(pwd)
        if h in targets:
            found[h] = pwd
            print("FOUND: %s:%s -> %s" % (targets[h], h, pwd))
            sys.stdout.flush()
            if len(found) == len(targets):
                break
        if i % 500000 == 0:
            pass  # no progress printing to keep it fast

if found:
    print("\n=== RESULTS ===")
    for h, username in targets.items():
        if h in found:
            print("%s (%s): %s" % (username, h, found[h]))
        else:
            print("%s (%s): NOT FOUND" % (username, h))
else:
    print("No passwords found in rockyou.txt")
