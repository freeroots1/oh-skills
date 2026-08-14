import hashlib, struct

h1 = "2d9d5942943a1323"
h2 = "79dca16741891333"

words = ["admin","admin123","admin888","123456","12345678","password","bjhzsv","bjhzsv.com","admin999","root","test","administrator","888888","123456789","admin000","111111","000000","pass","admin2016","admin2017","admin2018","admin2019","admin2020","admin2021","admin2022","admin2023","admin2024","admin2025","1234567890","qwerty","1q2w3e4r","abc123","letmein","welcome","monkey","dragon","master","sunshine","princess","baidu","alibaba","taobao","qq123","weixin","zhongguo","beijing","hangzhou","shenzhen","bjhz","hzsv","123456a","a123456","admin@123","passw0rd","woaini","1314520","5201314","asdfgh","zxcvbn","520520","7758521","wang123","zhang123","li123","admin123456","a123456789","12345","123qwe","qwe123","abc123456","admin666","admin777","admin555","admin222","admin333","admin111","admin444","password123","admin112233","passwd","Pass123","p@ssword","P@ssw0rd123","admin!@#","admin#123","1qaz2wsx","qazwsx","qwertyuiop","asdfghjkl","zxcvbnm","aaa123","bbb123","ccc123","test123","test1234","mima","mima123","sheji","wangzhan","guanli","guanliyuan","bjhzsvadmin","hzsva","bjadmin"]

def crc64_ecma(data):
    """CRC64-ECMA-182"""
    crc = 0
    poly = 0xC96C5795D7870F42
    for byte in data:
        crc ^= byte << 56
        for _ in range(8):
            if crc & (1 << 63):
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFFFFFFFFFFFFFFFF
    return crc

found = False

print("=== MD5 full + truncations ===")
for p in words:
    b = p.encode()
    for alg in [hashlib.md5, hashlib.sha1, hashlib.sha256, hashlib.sha224, hashlib.sha384, hashlib.sha512]:
        h = alg(b).hexdigest()
        for trunc in [lambda x:x[:16], lambda x:x[-16:], lambda x:x[8:24], lambda x:x[:8]+x[-8:]]:
            ht = trunc(h)
            if ht == h1:
                print(f"admin FOUND: {alg.__name__} trunc {p} -> {h}")
                found = True
            if ht == h2:
                print(f"admin999 FOUND: {alg.__name__} trunc {p} -> {h}")
                found = True

print("=== CRC64 ===")
for p in words:
    c = crc64_ecma(p.encode())
    h = f"{c:016x}"
    if h == h1:
        print(f"admin FOUND: CRC64 {p}")
        found = True
    if h == h2:
        print(f"admin999 FOUND: CRC64 {p}")
        found = True

print("=== Double MD5 ===")
for p in words:
    h = hashlib.md5(hashlib.md5(p.encode()).hexdigest().encode()).hexdigest()
    for trunc in [lambda x:x[:16], lambda x:x[-16:]]:
        ht = trunc(h)
        if ht == h1:
            print(f"admin FOUND: MD5(MD5) trunc {p} -> {h}")
            found = True
        if ht == h2:
            print(f"admin999 FOUND: MD5(MD5) trunc {p} -> {h}")
            found = True

print("=== MD5(username+password) ===")
for p in words:
    h = hashlib.md5(f"admin{p}".encode()).hexdigest()[:16]
    if h == h1:
        print(f"admin FOUND: MD5(admin+{p})[:16]")
        found = True
    h = hashlib.md5(f"admin999{p}".encode()).hexdigest()[:16]
    if h == h2:
        print(f"admin999 FOUND: MD5(admin999+{p})[:16]")
        found = True

print("=== MD5(password+salt) ===")
for p in words:
    for salt in ["bjhzsv","bjhzsv.com","admin","bj","hz","sv","123","888","pass","key","!@#$","2016","2017","2018","2019","2020"]:
        h = hashlib.md5(f"{p}{salt}".encode()).hexdigest()[:16]
        if h == h1:
            print(f"admin FOUND: MD5({p}+{salt})[:16]")
            found = True
        if h == h2:
            print(f"admin999 FOUND: MD5({p}+{salt})[:16]")
            found = True

if not found:
    print("No matches found.")
