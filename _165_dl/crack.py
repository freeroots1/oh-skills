import hashlib

hashes = ["2d9d5942943a1323", "79dca16741891333"]
users = ["admin", "admin999"]

passwords = [
    "admin", "admin123", "admin888", "admin@123", "admin123456",
    "bjhzsv", "bjhzsv888", "bjhzsv123", "beijing", "bjhz",
    "123456", "12345678", "123456789", "1234567890",
    "password", "pass123", "pass",
    "888888", "666666", "111111", "000000", "999999",
    "abc123", "abcd1234", "qwerty", "qwerty123",
    "master", "manager", "root", "system",
    "admin2011", "admin2012", "admin2013", "admin2014", "admin2015",
    "admin2016", "admin2017", "admin2018", "admin2019", "admin2020",
    "admin2021", "admin2022", "admin2023", "admin2024",
    "bjhzsv.com", "hzsv", "hongzuoshengwei",
    "123", "1234", "12345", "1234567",
    "123qwe", "qwe123", "1q2w3e", "1qaz2wsx",
    "iloveyou", "sunshine", "princess", "welcome",
    "monkey", "dragon", "football", "baseball",
    "abc123", "letmein", "trustno1", "passw0rd",
    "superman", "batman", "starwars",
    "nihao", "zhongguo", "beijing2008",
    "a123456", "a12345678", "a123456789",
    "aa123456", "aa12345678",
    "password1", "password123",
    "root123", "root1234", "root123456",
    "bjhzsv2011", "beijing2011",
    "tenglong", "tenglong888",
    "199-0888-8893", "19908888893",
    "13681449049", "01062489782",
]

# Try plain MD5
for p in passwords:
    h = hashlib.md5(p.encode()).hexdigest()[:16]
    if h in hashes:
        print(f"FOUND MD5: {p} -> {h}")

# Try md5(pass+user)
for u in users:
    for p in passwords:
        h = hashlib.md5(f"{p}{u}".encode()).hexdigest()[:16]
        if h in hashes:
            print(f"FOUND md5({p}{u}) -> {h}")
        h = hashlib.md5(f"{u}{p}".encode()).hexdigest()[:16]
        if h in hashes:
            print(f"FOUND md5({u}{p}) -> {h}")

# Try SHA1 truncated
for p in passwords:
    h = hashlib.sha1(p.encode()).hexdigest()[:16]
    if h in hashes:
        print(f"FOUND SHA1: {p} -> {h}")

print("Done")
